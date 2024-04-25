import os
import re
import csv

# extract from Result folder - Wrapper\logs\Results

''' output from the result - text file
GTYPPCS_R001::PASS
CONTACT_CHECK::PASS
APUBURST_R001::PASS
KILLSYSTEST::PASS
AIE2CHAR_R001::PASS
RPUBURST_R001::PASS
READ_DNA::PASS
'''

header0 = ["SN", "Timestamp","Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001','gtyppcs_r001']

# List of keys for the dictionary
header1 = ['SN','KILLSYSTEST','READ_DNA', 'CONTACT_CHECK', 'APUBURST_R001', 'RPUBURST_R001', 'AIE2CHAR_R001','GTYPPCS_R001']

def write_to_file(output):
    with open(filename, "w",newline='') as f:
        writer = csv.DictWriter(f, fieldnames= header1)
        writer.writeheader()
        writer.writerows(output)


files = []
filename = []
serialNo = []
# Get the current working directory
cwd = os.getcwd()
with os.scandir(cwd) as entries:
    for entry in entries:
        r1 = re.match(r"sn\w+\.txt",entry.name)
        if r1:
            #print(entry.name)
            files.append(entry.name)
            filename.append(r1.group())
        #print(entry.name)
print(filename)
print('Number of files: {0}'.format(len(filename)))
#======================================================================
#with open('snfile.txt', 'w') as f:
#    for line in filename:
#        f.write(line)
#        f.write('\n')
#======================================================================
for line in filename:
    r2 = re.match(r"sn(\w{16})",line)
    if r2:
        r2 = re.sub(r"sn(\w{16}).*",r"\1",line)
        #print(r2)
        serialNo.append(r2)
print(serialNo)
#===================================================================
# create a list of dic
m_dic = []

for key in serialNo:
    m_dic = key

print(m_dic)    #m_dic a list with all the serial no.
#To read in the first word of each line in a .txt file and store it in an array variable, where the value 
#associated with each element of the array is the next word in the line
data = {} # initialize an empty dict to store the data 
data2 = {}      
lis_dic = [] 
print("****************************************************")

for file in filename:
    r2 = re.match(r"sn(\w{16})",file)
    if r2:
        r2 = re.sub(r"sn(\w{16}).*",r"\1",file)
        #print(r2)
            
    with open(file,'r') as content:
        #data = {'S/N': 'Na', 'RPUBURST_R001': 'Na', 'READ_DNA': 'Na', 'APUBURST_R001': 'Na', 'AIE2CHAR_R001': 'Na', 'KILLSYSTEST': 'Na','CONTACT_CHECK':'Na'}
        data = {'SN': 'Na', 'RPUBURST_R001': 'Na', 'READ_DNA': 'Na', 'APUBURST_R001': 'Na', 'AIE2CHAR_R001': 'Na', 'KILLSYSTEST': 'Na','CONTACT_CHECK':'Na','GTYPPCS_R001':'Na'}
        data['SN'] = r2
        for line in content:
        # extract the desired value from the line
        #value = line.strip()
        # do something with the value - APUBURST_R003::FAIL
            words = line.strip().split("::")  # split the line into words
            key = words[0]  # get the first word as the key
            value = words[1]  # get the next word as the value
            if key in data:
                data[key] = value  # add the key-value pair to the dictionary

    #print(data)
    #data2[r2]=  data ; wrong concept
    lis_dic.append(data)
#==========================================================
#print("output of data2: ", data2)
print("output of lis_dic: ", lis_dic)
#print("output of data: ", data)
print("****************************************************")
'''
 [{'X128HGBOKYKLM9A2': {'APUBURST_R003': 'FAIL', 'READ_DNA': 'PASS', 'DPU_R001': 'FAIL', 'RPUBURST_R003': 'FAIL', 'LP5_R001': 'Na', 'PLNX_R001': 'Na'},
    'X4WPQDL0IDBB2FE1': {'APUBURST_R003': 'FAIL', 'READ_DNA': 'PASS', 'DPU_R001': 'PASS', 'RPUBURST_R003': 'FAIL', 'LP5_R001': 'Na', 'PLNX_R001': 'Na'},
''' 
# output into a csv file, using dic data above.
# Name of the CSV file to create
filename = 'example.csv'

# List of keys for the dictionary
#header = ['S/N','RPUBURST_R001','APUBURST_R001', 'AIE2CHAR_R001','READ_DNA', 'CONTACT_CHECK']

# Open the file in write mode
write_to_file(lis_dic)

print(f'Successfully wrote to {filename}')
