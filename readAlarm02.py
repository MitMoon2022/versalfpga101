# - The script is use to extract the log file from the robot PC generated log event alarm list. 
import os
import csv
import re
import time
import pandas as pd
from datetime import datetime   #for timestamp usage

# Read data from file
file_path =   r'Sept9Alarm.log'      #->r'C:\path\to\your\file\data.txt'  # Update this path with the actual path to your data file


wfilename = "fRobAlarmlog"
extension = "xlsx"
de_wfilename = "default"

header1=['NO', 'Code', 'Message', 'Count', 'Rate']


def generate_filename_with_unix_timestamp(prefix,extension):
    # Get current Unix timestamp
    unix_timestamp = int(time.time())
    # Concatenate prefix, timestamp, and extension
    filename = f"{prefix}_{unix_timestamp}.{extension}"
    return filename

de_wfilename=generate_filename_with_unix_timestamp(wfilename,extension)


def OutputExcel(de_wfilename, df):
    output_file_path = de_wfilename  # Update this path with the desired output file path
    df.to_excel(output_file_path, index=False)

cwd = os.getcwd()
files = os.listdir(cwd)

with open(file_path, 'r') as file:
    lines = file.readlines()

# Parse each line into the appropriate fields
parsed_data = []
for line in lines[1:]:  # Parse each line into the appropriate fields, skipping the first line
    try:
        parts = line.strip().split()

        print(f"Parts: {parts}")  # Debug: print the parts to see if they are correct
        no = int(parts[0])
        code = int(parts[1])
        count = int(parts[-2])
        rate = float(parts[-1].strip('%'))
        message = ' '.join(parts[2:-2])
        parsed_data.append([no, code, message, count, rate])

    except Exception as e:
        print(f"Error processing line: {line.strip()}")
        print(f"Exception: {e}")


# Create a DataFrame
df = pd.DataFrame(parsed_data, columns=header1)

# Display the DataFrame
#print(df)
OutputExcel(de_wfilename, df)

print(f'Data has been successfully written to {de_wfilename}')