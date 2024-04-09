'Extract log information -  apply at wrapper\log\top    XXX.log'

import os
import csv
import re
import time
from datetime import datetime   #for timestamp usage

wfilename = "fLogG_5-8"
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

def write_to_file(output):
    with open(de_wfilename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header4, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output)

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
        if 'apuburst_r001' in data and 'rpuburst_r001' in data and 'aie2char_r001' in data:
            if data['apuburst_r001'] == 'P' and data['rpuburst_r001'] == 'P' and data['aie2char_r001'] == 'P'and data['gtyppcs_r001'] == 'P':
                data['remark'] = 'PASS'
            else:
                data['remark'] = 'FAIL'
        else:
            data['remark'] = 'Na'

        lis_dic.append(data)
#============================================================================================================================

write_to_file(lis_dic)
print(f'Successfully wrote to {wfilename}')
