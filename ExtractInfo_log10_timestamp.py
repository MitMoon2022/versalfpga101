'Extract log information -  apply at wrapper\log\top    XXX.log'

import os
import csv
import re
import time
import pandas as pd
from datetime import datetime   #for timestamp usage

wfilename = "fLogG_5-10"
extension = "csv"
de_wfilename = "default"


header1 = ["SN", "Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001', 'STARTDT', 'ENDDT', 'remark']
#Remove the startDT and endDT
header1_1 = ["SN", "Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001','remark']

header2 = ["SN", "Test site","Chip Temperature",'DNA','read_dna','contact_check','STARTDT','ENDDT']

header3 = ["SN", "Timestamp","Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001','remark']

header4 = ["SN", "Timestamp","Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001','gtyppcs_r001','remark']

Param1 = "Versal_VC2802_ES1_LPNOM_ALL"
Param2 = "Versal_VC2802_ES1_LPNOM_CHK"

def write_to_file(output, de_wfilename):
    with open(de_wfilename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header4, extrasaction='ignore')
        writer.writeheader()
        #writer.writerows(output)
        #for i, row in enumerate(output):          #to clear the extra row at the beginning. i index starts from 0,1,2
        for i, row in enumerate(output.to_dict('records')):  # Convert DataFrame rows to dictionaries
            if i == 0 and not row.get('SN'):   # Skip the first row if it doesn't have a value for 'SN'
            #if i == 0 and (row['remark'] == 'Na' or row.get('SN', '')):   #Apply condition only for row 2
                print('skip')
                continue
            writer.writerow(row)
        #-----------------------------------------------------------------------------    
            #if row['remark'] != 'Na':  # Skip rows with 'remark' value 'Na'
            #    writer.writerow(row)
        #-----------------------------------------------------------------------------    
def generate_filename_with_unix_timestamp(prefix, extension):
    # Get current Unix timestamp
    unix_timestamp = int(time.time())
    # Concatenate prefix, timestamp, and extension
    filename = f"{prefix}_{unix_timestamp}.{extension}"
    return filename

de_wfilename=generate_filename_with_unix_timestamp(wfilename,extension)

cwd = os.getcwd()
files = os.listdir(cwd)

keys = ['SN', 'Test site']
lis_dic = []

R_filename = 'blank'        #Readin filename(initialize) in a loop to get the timestamp
infor_t=''
for file in files:
    if file.endswith('.log'):
        #---------------------------------------------------------------------------------------------------------------------------------
        R_filename = file
        # Define a regular expression pattern to match the desired information
        pattern = r'_(\d+)\.log$'
        # Use re.search() to find the pattern in the filename
        match = re.search(pattern, R_filename)
        if match:
            # Extract the desired information, in this case is the timestamp
            infor_t = match.group(1)
            #print("Extracted information:", infor_t)
            # converting timestamp to date
            dt_object = datetime.fromtimestamp(int(infor_t))
            print('Date and Time is:', dt_object)
        else:
            print("No match found")
#-----------------------------------------------------------------------------------------------------------------------------
        data = {}
        with open(os.path.join(cwd, file), 'r') as f:
            for line in f:
                if line.strip():        # Skip empty lines
                    words = line.strip().split(":")
                    if len(words) == 2:
                        key = words[0]
                        value = words[1]
                        data[key] = value.strip()
                    else:
                        key = words[0].replace('TEST', "").strip()
                        value = words[-1].replace('Result', "").replace("PASS", 'PASS').replace('1', 'PASS').replace("FAIL",'FAIL')
                        data[key] = value.strip()    
                data["Timestamp"] = (infor_t.strip())  # add the key-value pair to the dictionary                                                                                         
            # Adding the "remark" column based on specified keys
                if 'apuburst_r001' in data and 'rpuburst_r001' in data and 'aie2char_r001' in data and 'gtyppcs_r001' in data:
                    if data['apuburst_r001'] == 'PASS' and data['rpuburst_r001'] == 'PASS' and data['aie2char_r001'] == 'PASS'and data['gtyppcs_r001'] == 'PASS':
                        data['remark'] = 'PASS'
                    else:
                        data['remark'] = 'FAIL'
                else:
                    data['remark'] = 'Na'

        lis_dic.append(data)
#============================================================================================================================
#Sort the timestamp in ascending order
# Convert the list of dictionaries to a DataFrame with the specified column order
df = pd.DataFrame(lis_dic, columns=header4)

# Convert Timestamp column to numeric (if not already in numeric format)
df['Timestamp'] = pd.to_numeric(df['Timestamp'])

# Sort the DataFrame by the 'Timestamp' column
df_sorted = df.sort_values(by='Timestamp')

# Print the sorted DataFrame
print(df_sorted)

# If you want to save the sorted DataFrame to a CSV file
#sorted_file_path = './sorted_lis_dic.csv'
#df_sorted.to_csv(sorted_file_path, index=False)

#write_to_file(lis_dic)
write_to_file(df_sorted,de_wfilename)
print(f'Successfully wrote to {de_wfilename}')
