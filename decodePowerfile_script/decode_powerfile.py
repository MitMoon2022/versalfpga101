#!/usr/bin/env python3
import argparse
import json
import sys
from typing import List, Tuple, Optional

import pandas as pd
import numpy as np

def find_cond_header_row(df: pd.DataFrame) -> Optional[int]:
    """
    Locate the row index that marks the start of the data block:
    - First column cell equals '#Cond#'
    - Last column cell equals 'Comments' (case-insensitive match)
    Returns the row index, or None if not found.
    """
    if df.empty:
        return None
    last_col = df.columns[-1]
    for idx in range(len(df)):
        c0 = str(df.iat[idx, 0]).strip() if not pd.isna(df.iat[idx, 0]) else ""
        clast = str(df.iat[idx, df.shape[1] - 1]).strip() if not pd.isna(df.iat[idx, df.shape[1] - 1]) else ""
        if c0 == "#Cond#" and clast.lower() == "comments":
            return idx
    return None

def coerce_float(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if s.lower() in ("nan", "none", ""):
        return np.nan
    # Remove trailing 'V', commas, spaces
    s = s.replace(",", "")
    if s.endswith("V") or s.endswith("v"):
        s = s[:-1]
    try:
        return float(s)
    except Exception:
        return np.nan

def decode_powerfile(
    path: str,
    encoding: str = "utf-8-sig",
    delimiter: str = ",",
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Reads the PowerFile-style CSV and returns a tidy DataFrame with columns:
    - Rail (str)
    - Condition (str)
    - Voltage (float)
    Also returns a list of log messages about the parsing.
    """
    logs: List[str] = []
    # read with pandas; keep all columns
    df = pd.read_csv(path, encoding=encoding, dtype=str, header=0, sep=delimiter, engine="python")
    logs.append(f"Loaded CSV shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Detect the condition header row
    cond_hdr = find_cond_header_row(df)
    if cond_hdr is None:
        # Fallback heuristic: try the first row where last column equals 'Comments'
        last_col_vals = df.iloc[:, -1].astype(str).str.strip().str.lower()
        candidates = df.index[last_col_vals == "comments"].tolist()
        if candidates:
            cond_hdr = candidates[-1]
            logs.append(f"Condition header fallback used at row {cond_hdr}.")
        else:
            raise RuntimeError("Could not find the '#Cond#' header row with 'Comments' in last column.")

    # Use the condition header row to rename columns (rail names)
    header_row = df.iloc[cond_hdr]
    rails = header_row.tolist()
    # First column is '#Cond#', last is 'Comments'; rail names are in columns [1:-1]
    if str(rails[0]).strip() != "#Cond#" or str(rails[-1]).strip().lower() != "comments":
        logs.append("Warning: header row did not exactly match ['#Cond#', ..., 'Comments']; proceeding anyway.")
    # Build new column names
    new_cols = []
    for j, col in enumerate(df.columns):
        if j == 0:
            new_cols.append("#Cond#")
        elif j == df.shape[1] - 1:
            new_cols.append("Comments")
        else:
            name = str(header_row.iloc[j]).strip() if not pd.isna(header_row.iloc[j]) else f"Col{j}"
            new_cols.append(name if name else f"Col{j}")
    df.columns = new_cols
    logs.append(f"Detected {len(new_cols)-2} rail columns.")

    # Data rows start after the header row, continue until we detect end (all-NaN data rows)
    data_block = df.iloc[cond_hdr + 1 :].copy()

    # Keep only the rail columns and the Comments column
    rail_cols = [c for c in df.columns if c not in ("#Cond#", "Comments")]
    if not rail_cols:
        raise RuntimeError("No rail columns detected.")
    if "Comments" not in df.columns:
        raise RuntimeError("Comments column not found after renaming.")
    # Drop rows that have neither a comment nor any numeric values
    # First, coerce numeric in rail columns
    for c in rail_cols:
        data_block[c] = data_block[c].apply(coerce_float)

    # Identify rows that have at least one numeric value across rails or a comment label
    has_any_val = data_block[rail_cols].apply(lambda r: np.any(~np.isnan(r.values)), axis=1)
    comment_labels = data_block["Comments"].fillna("").astype(str).str.strip()
    has_comment = comment_labels != ""

    # Cut off after the last "useful" row
    if has_any_val.any() or has_comment.any():
        last_idx = max(data_block.index[has_any_val | has_comment].tolist())
        data_block = data_block.loc[data_block.index.min() : last_idx]
    else:
        logs.append("No data rows with values or comments detected.")
        data_block = data_block.iloc[0:0]

    # Prepare long/tidy output
    records = []
    for idx, row in data_block.iterrows():
        cond = str(row.get("Comments", "") or "").strip()
        if not cond:
            # Sometimes condition label may appear in first col (rare), but in this format we expect 'Comments'
            cond = ""
        for rail in rail_cols:
            v = row[rail]
            if pd.isna(v):
                continue
            records.append({"Rail": rail, "Condition": cond, "Voltage": float(v)})

    out_df = pd.DataFrame.from_records(records, columns=["Rail", "Condition", "Voltage"])
    logs.append(f"Decoded {len(out_df)} (rail, condition, voltage) entries across {out_df['Rail'].nunique()} rails and {out_df['Condition'].nunique()} conditions.")
    return out_df, logs

def main():
    ap = argparse.ArgumentParser(description="Decode voltage rails from a PowerFile-style CSV into Rail/Condition/Voltage.")
    ap.add_argument("--csv", required=True, help="Path to PowerFile.csv")
    ap.add_argument("--output-csv", help="Path to write decoded CSV (Rail,Condition,Voltage)")
    ap.add_argument("--output-json", help="Path to write decoded JSON")
    ap.add_argument("--delimiter", default=",", help="CSV delimiter (default: ',')")
    ap.add_argument("--encoding", default="utf-8-sig", help="File encoding (default: utf-8-sig)")
    args = ap.parse_args()

    try:
        decoded, logs = decode_powerfile(args.csv, encoding=args.encoding, delimiter=args.delimiter)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Write outputs
    if args.output_csv:
        decoded.to_csv(args.output_csv, index=False)
    else:
        # Print to stdout
        decoded.to_csv(sys.stdout, index=False)

    if args.output_json:
        # Write JSON grouped by rail for readability
        grouped = {}
        for rail, sub in decoded.groupby("Rail"):
            grouped[rail] = [{"Condition": c, "Voltage": float(v)} for c, v in zip(sub["Condition"], sub["Voltage"])]
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(grouped, f, indent=2)

    # Log summary to stderr
    for line in logs:
        print(line, file=sys.stderr)

if __name__ == "__main__":
    main()

