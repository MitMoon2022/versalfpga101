'Extract log information -  apply at wrapper\log\top    XXX.log'
import os
import csv
import re
#folder_path = '/path/to/folder'
#files = os.listdir(folder_path)

filename = "fileLogm1_2.csv"

def write_to_file(output):
    with open(filename,"w",newline='') as f:
        writer = csv.DictWriter(f, fieldnames= ["SN", "Test site","Chip Temperature","killsystest",'read_dna','rpuburst_r001','apuburst_r001','aie2char_r001','contact_check','STARTDT','ENDDT'],extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output)

# Get the current working directory
cwd = os.getcwd()
print(cwd)
files = os.listdir(cwd)
print(files)



keys = ['SN', 'Test site']
lis_dic = []    # to store a list of dict
for file in files:
    if file.endswith('.log'):
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
                    #print("len of words is ", len(words))
                    #print("show words: ", words)
                    key = words[0].replace('TEST',"").strip()
                    value = words[-1].replace('Result',"").replace("PASS",'P').replace('1','P').replace("FAIL",'F')
                    #Start from here to check the key? Modify to include the Main Param Name
                    if key == "Versal_VC2802_ES1_LPNOM_ALL":        # Replace with the main program name for different project
                        print("Found!\n")
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