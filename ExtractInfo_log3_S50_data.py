'Extract log information -  apply at wrapper\log\top    XXX.log'
import os
import csv
import re
#folder_path = '/path/to/folder'
#files = os.listdir(folder_path)

from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d%m%Y%H%M%S")
print("date and time =", dt_string)

filename = f"fileLogm1_XA_{dt_string}.csv"
print(filename)

def write_to_file(output):
    with open(filename,"w",newline='') as f:
        writer = csv.DictWriter(f, fieldnames= ["SN", "Test site","Chip Temperature","killsystest",'read_dna','all_lpnom_r001','contact_check','STARTDT','ENDDT'],extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output)

cwd = os.getcwd()
print("Current working directory:", cwd)

# Specify the subdirectory where you want to extract the files (e.g., "data")
subdirectory = "data"

# Create the full path to the destination directory using os.path.join()
data_directory = os.path.join(cwd, subdirectory)
print("Data directory:", data_directory)

# List the files in the data_directory
files = os.listdir(data_directory)
print("Files in data directory:", files)



keys = ['SN', 'Test site']
lis_dic = []    # to store a list of dict
for file in files:
    if file.endswith('.log'):
        data = {} # initialize an empty dict to store the data 
        with open(os.path.join(data_directory, file), 'r') as f:
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
                    #print("len of words is ", len(words))
                    #print("show words: ", words)
                    key = words[0].replace('TEST',"").strip()
                    value = words[-1].replace('Result',"").replace("PASS",'P').replace('1','P').replace("FAIL",'F')
                    #Start from here to check the key? Modify to include the Main Param Name
                    if key == "all_lpnom_r001":        # Replace with the main program name for different project
                        data[key] = (value.strip())  # add the key-value pair to the dictionary
                        print("Found-key with value: ", value)
                        #val_time = re.sub(r'.*START (.*)::End(.*)::Result.*',r'\1\2',line)  #2nd arguements - subsituate with (1) or (2) by \1 or \1\2
                        val_time_start = re.sub(r'.*START (.*)::End(.*)::Result.*',r'\1',line)  #2nd arguements - subsituate with (1) or (2) by \1 or \1\2
                        val_time_end = re.sub(r'.*START (.*)::End(.*)::Result.*',r'\2',line) 
                        print('key', key,' and val_time_start:', val_time_start, 'val_End: ',val_time_end)
                        #print('val_time:',val_time.strip())
                        key_S = "STARTDT"
                        key_E = "ENDDT"
                        data[key_S] = (val_time_start);
                        data[key_E] = (val_time_end);
                    else:
                        data[key] = (value.strip())  # add the key-value pair to the dictionary

        lis_dic.append(data)  

#print("Final result:",lis_dic)      

write_to_file(lis_dic)
print(f'Successfully wrote to {filename}')