import pandas as pd
import sys
import datetime
import os

# File date for the output Excel
filedate = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# === CONFIG ===
# You can modify these if not using command-line args
input_excel = 'summary_Local_20250803-111019.xlsx'
sheet_to_process = 'Result_Summary'

# Test column range (inclusive)
test_start_col = 'contact_check_lp5_LP5_MC3'
test_end_col = 'RPUBURST_VST'

# Output Excel file (you can overwrite input if desired)
#output_excel = input_excel.replace('.xlsx', '_with_overall.xlsx')
# Directory containing JSON files
directory = './'                        #Create a Result folder and dump your data (json) file into it.
output_excel = f'uniqueSN_summary{filedate}.xlsx'

# === MAIN FUNCTION ===
def generate_overall_tab(input_excel, sheet_name):
    df = pd.read_excel(input_excel, sheet_name=sheet_name)

    # Ensure Serial_Number is present
    if 'Serial_Number' not in df.columns:
        raise ValueError("Serial_Number column not found in the sheet")

    # Get the test columns between start and end
    columns = df.columns.tolist()
    try:
        start_idx = columns.index(test_start_col)
        end_idx = columns.index(test_end_col)
    except ValueError:
        raise ValueError("Test columns not found in the specified range")

    test_columns = columns[start_idx:end_idx + 1]

    # Build the overall dataframe
    overall_df = pd.DataFrame(columns=['Serial_Number'] + test_columns)

    for sn, group in df.groupby('Serial_Number'):
        overall_row = {'Serial_Number': sn}
        test_results = []
        fail_reasons = []

        for col in test_columns:
            values = group[col].dropna().astype(str).str.lower().str.strip()

            if 'pass' in values.values:
                result = 'pass'
            elif 'fail' in values.values:
                result = 'fail'
                fail_reasons.append(col)
            else:
                result = ''
                fail_reasons.append(col)

            overall_row[col] = result
            test_results.append(result)
                
        # Add Remark and Fail_Reason
        if all(r == 'pass' for r in test_results):
            overall_row['Remark'] = 'pass'
            overall_row['Fail_Reason'] = ''
        else:
            overall_row['Remark'] = 'fail'
            overall_row['Fail_Reason'] = ', '.join(fail_reasons)
                
        
        #overall_df = pd.concat([overall_df, pd.DataFrame([overall_row])], ignore_index=True)
        overall_df = pd.concat([overall_df, pd.DataFrame([overall_row])], ignore_index=True)

    # Write to Excel (append to original file or create new one)
    #with pd.ExcelWriter(output_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    with pd.ExcelWriter(output_excel, engine='openpyxl', mode='w') as writer:
            overall_df.to_excel(writer, sheet_name='Overall', index=False)

    print(f"✅ 'Overall' sheet written to {output_excel}")


# === RUN SCRIPT ===
if __name__ == '__main__':
    # Optional command-line arguments
    if len(sys.argv) == 3:
        input_excel = sys.argv[1]
        sheet_to_process = sys.argv[2]

    generate_overall_tab(input_excel, sheet_to_process)
