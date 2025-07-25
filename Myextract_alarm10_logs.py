import os
import re
import pandas as pd
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

wfilename = "ICJam_Alarm_Barcode_v2"
extension = "xlsx"

def generate_filename_with_unix_timestamp(prefix, extension):
    # Get current Unix timestamp
    unix_timestamp = int(time.time())
    # Concatenate prefix, timestamp, and extension
    filename = f"{prefix}_{unix_timestamp}.{extension}"
    return filename

de_wfilename=generate_filename_with_unix_timestamp(wfilename,extension)

# -------------------------------
# Step 1: Parse log files
# -------------------------------

#log_directory = "./Logs"
script_dir = os.path.dirname(os.path.abspath(__file__)) #edited so that it will run even in home dir
log_directory = os.path.join(script_dir, 'Logs') #edited so that it will run even in home dir

#alarm_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d+)? - .* - INFO - <<ALARM%(\d+)%(.+?)>>")
alarm_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:,\d+)? - .* - INFO - <<ALARM%(\d+)%(.+?)>>")
sot_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:,\d+)? - .* - INFO - <<(\d+)%SOT>>")
eot_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:,\d+)? - .* - INFO - <<(\d+)%EOT%(\d+)>>")
# Define the pattern for the barcode
#barcode_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - INFO - BARCODE:(.+?)$")
#date_search = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})") #Date search
date_search = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:,\d+)?") #Date search


alarm_data = []
barcode_data = []


for robot_folder in os.listdir(log_directory):
    robot_path = os.path.join(log_directory, robot_folder)
    print(robot_folder)
    if not os.path.isdir(robot_path) or not robot_folder.startswith("Robot"):
        continue

    for date_folder in os.listdir(robot_path):
        date_path = os.path.join(robot_path, date_folder)
        if not os.path.isdir(date_path):
            continue

        for log_file in os.listdir(date_path):
            log_path = os.path.join(date_path, log_file)
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    current_slot = None  # Track current active slot

                    # Track barcodes per site (1-4)
                    site_barcode = {1: None, 2: None, 3: None, 4: None}

                    for line in f:
                        match_alarm = alarm_pattern.search(line)
                        # date_match = date_search.match(line)
                        # if date_match:
                        #    date = date_match.group(1)
                        #    print(date)
                        if match_alarm:
                            date, alarm_code, alarm_msg = match_alarm.groups()
                            alarm_data.append([date, f"<<ALARM%{alarm_code}%{alarm_msg}>>", alarm_code, alarm_msg])
                            continue

                        match_sot = sot_pattern.search(line)
                        if match_sot:
                            date, site_no = match_sot.groups()
                            current_slot = int(site_no)
                            alarm_data.append([date, f"<<{site_no}%SOT>>", "SOT", f"SLT1 Site{site_no} Insertion"])
                            continue

                        match_eot = eot_pattern.search(line)
                        if match_eot:
                            date, site_no, result = match_eot.groups()
                            site_no_int = int(site_no)
                            result_text = f"Pass-{site_no}" if result == "1" else f"Fail-{site_no}"
                             # If a barcode was saved for this site, append it
                            if site_no_int in site_barcode and site_barcode[site_no_int]:
                                combined_result = f"{result_text}-{site_barcode[site_no_int]}"
                                alarm_data.append([date, f"<<{site_no}%EOT>>", "EOT", combined_result])
                                # Clear barcode after use
                                site_barcode[site_no_int] = None
                            else:
                                alarm_data.append([date, f"<<{site_no}%EOT>>", "EOT", result_text])
                            continue

                           
                        if "BARCODE:" in line and current_slot is not None:
                              date_match = date_search.match(line)
                              if date_match:
                                 date = date_match.group(1)
                                 #print(date)
                              barcode_values = line.strip().split(",")
                              if len(barcode_values) >= current_slot:
                                    barcode = barcode_values[-current_slot]
                                    barcode_data.append([date, current_slot, barcode])
                                    # Also add to alarm_data with Alarm Code as 'barcode'
                                    alarm_data.append([date, f"BARCODE", "barcode", barcode])

                                    # Save barcode for this site number
                                    if current_slot in site_barcode:
                                        site_barcode[current_slot] = barcode

            except Exception as e:
                print(f"Error reading {log_path}: {e}")

# Convert to DataFrames
df_alarm = pd.DataFrame(alarm_data, columns=["Date", "Alarm", "Alarm Code", "Alarm Message"])
df_barcode = pd.DataFrame(barcode_data, columns=["Date", "SiteX", "Barcode"])

# Convert numeric-looking strings to numbers where appropriate
#df_alarm["Alarm Code"] = pd.to_numeric(df_alarm["Alarm Code"], errors='ignore')
#df_alarm["Alarm Message"] = pd.to_numeric(df_alarm["Alarm Message"], errors='ignore')
df_alarm["Alarm Code"] = df_alarm["Alarm Code"].astype(str)
df_alarm["Alarm Message"] = df_alarm["Alarm Message"].astype(str)
#df_alarm["Alarm Message"] = df_alarm["Alarm Message"].astype(str)
#============================================================================================================
# Merge DataFrames on the 'Date' column
df_Alarm_barcode = pd.merge(df_alarm, df_barcode, on='Date', how='outer')
#df_Alarm_barcode["Alarm Message"] = df_Alarm_barcode["Alarm Message"].astype(str)
# Sort by 'Date' column
df_Alarm_barcode = df_Alarm_barcode.sort_values(by='Date')
#df_Alarm_barcode["Alarm Code"] = df_Alarm_barcode["Alarm Code"].astype(str)
# Reset index
df_Alarm_barcode = df_Alarm_barcode.reset_index(drop=True)

# Save both to a single Excel file
with pd.ExcelWriter(de_wfilename, engine="xlsxwriter") as writer:
    df_alarm.to_excel(writer, sheet_name="AlarmSotEot", index=False)
    df_barcode.to_excel(writer, sheet_name="Barcodes", index=False)
    df_Alarm_barcode.to_excel(writer, sheet_name="AlarmBarcode", index=False)

#print("Saved: extracted_IC_Jam_Alarmlogs_Barcode.xlsx")
print(f"Saved: {de_wfilename}")
