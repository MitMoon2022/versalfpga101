'Extract log information -  apply at wrapper\log\top    XXX.log'
import os
import csv
import re
import sys
import datetime
import pandas as pd

#log_file_path = "path/to/your/logfile.log"
log_file_path = "path/to/your/"
input_filename = "\\run_summary.log"        #is \\ for esc, not 1 backslash.

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%d%m%Y_%H%M%S") #Tested!

print(formatted_datetime)   #check only

output_filename = f"XASummaryLogf_{formatted_datetime}.xlsx"
# Get the current working directory
cwd = os.getcwd()
print(cwd)
files = os.listdir(cwd)
#print(files)

# Testing in local dir first:
log_file_path = cwd
full_path = log_file_path+input_filename
print("fullPath: ",full_path)

# Accessing command-line arguments
script_name = sys.argv[0]
arg1 = sys.argv[1] if len(sys.argv) > 1 else None
#arg2 = sys.argv[2] if len(sys.argv) > 2 else None

print("Script name:", script_name)
print("Argument 1:", arg1)      
#print("Argument 2:", arg2)

#print(type(arg1))
#startLine = int(arg1)    #The starting number line where it starts to collecting the data. 
#print(startLine)

if arg1:
    startLine = int(arg1)    #The starting number line where it starts to collecting the data. 
else:
    print("arg1 is None")
    startLine = 1

# Create an empty DataFrame with the desired column names 
# Serial No.	DNA	Timestamp	Site	Borad SN	CC	APU	RPU	AIE	PCIE	DDR

columns = ["Serial No.", "DNA", "Timestamp","Site","Board Sn", "CC", "APU","RPU","AIE","PCIE","DDR","Result"]  # Customize column names
df = pd.DataFrame(columns=columns)


try:
    with open(full_path, "r") as log_file:
        for line_number, line in enumerate(log_file, start=1):
            if line_number < startLine:
                #Skip the define no. of lines
                continue
            
            # Process each line and split it into columns as needed
            line_data = line.split(",")  # Adjust the delimiter as per your log file format

            # Create a dictionary to match the data with the columns
            data_dict = {col: val for col, val in zip(columns, line_data)}

            # Append the data as a new row to the DataFrame
            # The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
            #df = df.append(data_dict, ignore_index=True) 
            
             # Append the data as a new row to a temporary DataFrame
            temp_df = pd.DataFrame([data_dict])

            # Concatenate the temporary DataFrame with the main DataFrame
            df = pd.concat([df, temp_df], ignore_index=True)

    
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
