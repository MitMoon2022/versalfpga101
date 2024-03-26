'Extract log information -  apply at wrapper\log\top    XXX.log'
import os
import csv
import re
from datetime import datetime   #for timestamp usage

#folder_path = '/path/to/folder'
#files = os.listdir(folder_path)

filename = "ExtLog_ES2_B0_R7.csv" #Change your filename accordingly

#header1 is used previously before 2/15
header1 = ["SN", "Test site","Chip Temperature","DNA",'read_dna','tenzing2_5mc_r004','plnx_r003','hnicx_r003','apuburst_r004',
                                                'rpuburst_r004','dpu_r002','lp5_delay_r001','lp5_c1_r003','lp5_dr_r004','lp5_dqsgate_r001']
#header2 is used previously after 2/15 - Testing for LP5
header2 = ["SN","Test site","Chip Temperature","DNA",'read_dna','tenzing2_5mc_r004','lp5_dqsgate_r001','lp5_dr_r004']

#change from lp5_dr_r003 to lp_dr_r004

header3 = ["SN", "Test site","Chip Temperature","DNA",'read_dna','tenzing2_5mc_r004','plnx_r003','hnicx_r003','apuburst_r004',
                                                'rpuburst_r004','dpu_r002','lp5_delay_r001','lp5_c1_r003','lp5_dr_r004','lp5_dqsgate_r001',
                                                'STARTDT','ENDDT']

header4 = ["SN", "Timestamp","Test site","Chip Temperature","DNA",'read_dna','tenzing2_5mc_r004','plnx_r003','hnicx_r003','apuburst_r004',
                                                'rpuburst_r004','dpu_r002','lp5_delay_r001','lp5_c1_r003','lp5_dr_r004','lp5_dqsgate_r001']
Param1 = "VN3716_KSB_ES2" #VN3716_KSB_ES2
Param2 = ""


def write_to_file(output):
    with open(filename,"w",newline='') as f:
        writer = csv.DictWriter(f, fieldnames= header4,extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output)

# Get the current working directory
cwd = os.getcwd()
print(cwd)
files = os.listdir(cwd)
#print(files)

R_filename = 'blank'

keys = ['SN', 'Test site']
lis_dic = []    # to store a list of dict
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
        data = {} # initialize an empty dict to store the data 
        with open(os.path.join(cwd, file), 'r') as f:
            for line in f:
                words = line.strip().split(":")  # split the line into words
                #condition of the len of words (list).
                if len(words)==2:
                    key = words[0]  # get the first word as the key eg. SN: XXXXXXXX
                    value = words[1]  # get the next word as the value
                    data[key] = (value.strip())  # add the key-value pair to the dictionary
                    #print("show: ",data)   
                    # extract information from text
                else:
                    key = words[0].replace('TEST',"").strip()
                    value = words[-1].replace('Result',"").replace("PASS",'PASS').replace('1','PASS').replace("FAIL",'FAIL')
                    #print('key', key,' and value', value)
                    data[key] = (value.strip())  # add the key-value pair to the dictionary
            data["Timestamp"] = (infor_t.strip())  # add the key-value pair to the dictionary
            

                    
        lis_dic.append(data)  

#print("Final result:",lis_dic)      

write_to_file(lis_dic)
print(f'Successfully wrote to {filename}')