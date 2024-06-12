'Extract log information -  apply at wrapper\log\top    XXX.log'

#import numpy as np
#import matplotlib.pyplot as plt
#import panda as pd
import os
import csv
import re
import time
import argparse
import time
import datetime as dt
from datetime import datetime   #for timestamp usage

wfilename = "SV60-execution-report"
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

### Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument ("-f", "--From", help = "Start Date")
parser.add_argument("-t", "--To", help = "End Date")
## Read arguments from the command line
args = parser.parse_args()

if(args.From):
    startDate = args.From
    startDate_obj = datetime.strptime(startDate, '%Y-%m-%d')
if(args.To):
    endDate = args.To
    endDate_obj = datetime.strptime(endDate, '%Y-%m-%d')
        
print("SV60 VST Execution Report from", startDate_obj, "to", endDate_obj)

filename = wfilename + "-from-" + startDate + "-to-" + endDate

def write_to_file(output):
    with open(de_wfilename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header4, extrasaction='ignore')
        writer.writeheader()
        #writer.writerows(output)
        for i, row in enumerate(output):          #to clear the extra row at the beginning. i index starts from 0,1,2
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

de_wfilename=generate_filename_with_unix_timestamp(filename,extension)

cwd = '/group/xap_charserv2/engineering/Characterization/charmnt/Robot-SLT/XAP/SLT-01/Project/Versal/H1760/ES2/VST_TP_REPO2/Wrapper/logs/top'
files = os.listdir(cwd)

keys = ['SN', 'Test site']
lis_dic = []
R_filename = 'blank'        #Readin filename(initialize) in a loop to get the timestamp
infor_t=''
for file in files:
    if file.endswith('.log'):
        R_filename = file
        # Define a regular expression pattern to match the desired information
        pattern = r'_(\d+)\.log$'
        # Use re.search() to find the pattern in the filename
        match = re.search(pattern, R_filename)
        if match:
            infor_t = match.group(1)
            dt_object = dt.datetime.fromtimestamp(int(infor_t))
            if( (dt_object > startDate_obj) and  (dt_object < endDate_obj)):
                #print('Date and Time is:', dt_object)
                #print(R_filename)
                data = {}
                with open(os.path.join(cwd, R_filename), 'r') as f:
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
        else:
            print('no match found')

#============================================================================================================================
## STATISTIC PRINT 

CC_PASS_COUNT = 0
APUBURST_PASS_COUNT = 0
APUBURST_FAIL_COUNT = 0
APUBURST_FAIL_UNIT = []

RPUBURST_PASS_COUNT = 0
RPUBURST_FAIL_COUNT = 0
RPUBURST_FAIL_UNIT = []

AIE2CHAR_PASS_COUNT = 0
AIE2CHAR_FAIL_COUNT = 0
AIE2CHAR_FAIL_UNIT = []

GTYPPCS_PASS_COUNT = 0
GTYPPCS_FAIL_COUNT = 0
GTYPPCS_FAIL_UNIT = []

for contactchk in lis_dic:
	if(contactchk.get('contact_check') == 'PASS'):
	    CC_PASS_COUNT += 1


for apuburst in lis_dic:
    
    if(apuburst.get('apuburst_r001') == 'PASS'):
        APUBURST_PASS_COUNT += 1
    if(apuburst.get('apuburst_r001') == 'FAIL'):
        APUBURST_FAIL_COUNT += 1
        APUBURST_FAIL_UNIT.append(apuburst.get('SN'))

for rpuburst in lis_dic:

    if(rpuburst.get('rpuburst_r001') == 'PASS'):
        RPUBURST_PASS_COUNT += 1
    if(rpuburst.get('rpuburst_r001') == 'FAIL'):
        RPUBURST_FAIL_COUNT += 1
        RPUBURST_FAIL_UNIT.append(rpuburst.get('SN'))

for aie2char in lis_dic:

    if(aie2char.get('aie2char_r001') == 'PASS'):
        AIE2CHAR_PASS_COUNT += 1
    if(aie2char.get('aie2char_r001') == 'FAIL'):
        AIE2CHAR_FAIL_COUNT += 1
        AIE2CHAR_FAIL_UNIT.append(aie2char.get('SN'))

for gtyppcs in lis_dic:
    if(gtyppcs.get('gtyppcs_r001') == 'PASS'):
        GTYPPCS_PASS_COUNT += 1
    if(gtyppcs.get('gtyppcs_r001') == 'FAIL'):
        GTYPPCS_FAIL_COUNT += 1
        GTYPPCS_FAIL_UNIT.append(gtyppcs.get('SN'))
        

total_sample = len(lis_dic)

print("Statistical Summary")
print("Total unit executed : " + str(CC_PASS_COUNT))

print("\n")
print("APU BURST (R001)  Pass Count : " + str(APUBURST_PASS_COUNT))
print("APU BURST (R001) Fail Count : " + str(APUBURST_FAIL_COUNT))
print("APU BURST (R001) Fail Unit :\n" + str(APUBURST_FAIL_UNIT) + "\n")

print("\n")
print("RPU BURST (R001)  Pass Count : " + str(RPUBURST_PASS_COUNT))
print("RPU BURST (R001) Fail Count : " + str(RPUBURST_FAIL_COUNT))
print("RPU BURST (R001) Fail Unit :\n" + str(RPUBURST_FAIL_UNIT) + "\n")

print("\n")
print("AIE2CHAR (R001)  Pass Count : " + str(AIE2CHAR_PASS_COUNT))
print("AIE2CHAR (R001) Fail Count : " + str(AIE2CHAR_FAIL_COUNT))
print("AIE2CHAR (R001) Fail Unit :\n" + str(AIE2CHAR_FAIL_UNIT) + "\n")

print("\n")
print("GTYPPCS (R001)  Pass Count : " + str(GTYPPCS_PASS_COUNT))
print("GTYPPCS (R001) Fail Count : " + str(GTYPPCS_FAIL_COUNT))
print("GTYPPCS (R001) Fail Unit :\n" + str(GTYPPCS_FAIL_UNIT) + "\n")
print("\n")

write_to_file(lis_dic)
print(f'Successfully wrote to {de_wfilename}')
