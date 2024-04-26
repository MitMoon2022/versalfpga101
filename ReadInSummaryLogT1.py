'Extract log information -  apply at wrapper\log\top    XXX.log'
import os
import csv
import re
import pandas as pd

#log_file_path = "path/to/your/logfile.log"
log_file_path = "path/to/your/"
input_filename = "\\run_summary.log"        #is \\ for esc, not 1 backslash.


output_filename = "ReadSummaryLogf_1.xlsx"
# Get the current working directory
cwd = os.getcwd()
print(cwd)
files = os.listdir(cwd)
#print(files)

# Testing in local dir first:
log_file_path = cwd
full_path = log_file_path+input_filename
print("fullPath: ",full_path)


# Create an empty DataFrame with the desired column names 
# Serial No.	DNA	Timestamp	Site	Borad SN	CC	APU	RPU	AIE	PCIE	DDR

columns = ["Serial No.", "DNA", "Timestamp","Site","Board Sn", "CC", "APU","RPU","AIE","PCIE","DDR","Result"]  # Customize column names
df = pd.DataFrame(columns=columns)


try:
    with open(full_path, "r") as log_file:
        for line in log_file:
            
            # Process each line and split it into columns as needed
            line_data = line.split(",")  # Adjust the delimiter as per your log file format

            # Create a dictionary to match the data with the columns
            data_dict = {col: val for col, val in zip(columns, line_data)}

            # Append the data as a new row to the DataFrame
            df = df.append(data_dict, ignore_index=True)
    
    # Now you have a DataFrame containing the log data
    #print(df)
    df.to_excel(output_filename, index=False)
    

    #df = pd.read_csv(log_file_path)  # Assumes log data is in CSV format
    #df.to_excel(output_filename, index=False)
    #print(f"Log data has been written to {output_filename}.")
#//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++






except FileNotFoundError:
    print(f"The file {log_file_path} does not exist.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
