import openpyxl
from datetime import datetime
from itertools import repeat

# Sample log data (replace this with your actual log data)
log_data = """
# ... (your log data here)
"""
i_filename = 'sample_sum.log'   #input file to be extracted.
# Read log data from the 'sample_sum.log' file
with open(i_filename, 'r') as file:
    log_data = file.read()

o_filename = "ExtLog_ES2B0_summary.xlsx" #Change your filename accordingly

head_keys = ['TENZING2_5MC_R004', 'RPUBURST_R003', 'APUBURST_R003', 'LP5_DR_R003', 'LP5_DELAY_R001', 'HNICX_R002', 'DPU_R002', 'LP5_C1_R003', 'READ_DNA', 'PLNX_R003', 'TENZING2_5MC_R003', 'RPUBURST_R002', 'APUBURST_R002', 'LP5_C1_R002', 'LP5_DR_R002', 'LP5_DR_R004']
data = {k:'NA' for k in head_keys}
# printing result
print("data : " + str(data))
print("len of data : " ,len(data))

lis_dic1 = []    # to store a list of dict of entry_dict
lis_dic2 = []    # to store a list of dict of data

# Store log entry as a dictionary
entry_dict = {
    "Serial Number": 'NA',
    "Location": 'NA',
    "Test Station": 'NA',
    "Timestamp": 'NA' + ' ' + 'NA'
    #"Tests": []  # Initialize an empty list to store tests
}

# Process log data and write to the sheet
log_entries = [entry.strip().split() for entry in log_data.strip().split('\n')]
#print(log_entries)
# Iterating through the list of lists
for row in log_entries:
    print("row= ",row)
    entry_dict = {
    "Serial Number": row[0],
    "Location": row[1],
    "Test Station": row[2],
    "Timestamp": row[3] + ' ' + row[4]
    }
    lis_dic1.append(entry_dict)
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    head_keys = ['TENZING2_5MC_R004', 'RPUBURST_R003', 'APUBURST_R003', 'LP5_DR_R003', 'LP5_DELAY_R001', 'HNICX_R002', 'DPU_R002', 'LP5_C1_R003', 'READ_DNA', 'PLNX_R003', 'TENZING2_5MC_R003', 'RPUBURST_R002', 'APUBURST_R002', 'LP5_C1_R002', 'LP5_DR_R002', 'LP5_DR_R004']
    data = {k:'NA' for k in head_keys}  #Need to re-intialize the dic_data for every loop.
    # Process tests and add to the dictionary
    for test_result in row[5:]:
        test_name, result = test_result.split("::")
        #print("test_name: ", test_name)
        #print("result: ", result)
        data[test_name] =result
        #print("show Data: " + str(data))
        #data["Tests"].append({test_name: result})

    lis_dic2.append(data)
#**************************************************************************************


#------------------ checking -------------------------------------------
"""     
print(lis_dic1)
print("Size of a list_1: ", len(lis_dic1))
print("---------------------------------------------------------------------")
print(lis_dic2)
print("Size of a list_2: ", len(lis_dic2))
#print("row5 of dic2: ", lis_dic2[4])
"""

# Create a new Excel workbook and add a worksheet
workbook = openpyxl.Workbook()
worksheet = workbook.active

# Define headers for the worksheet
headers = ["Serial Number", "Location", "Test Station", "Timestamp"] + head_keys

# Write headers to the worksheet
worksheet.append(headers)

# Combine data from lis_dic1 and lis_dic2 and write to the worksheet
for entry, data_row in zip(lis_dic1, lis_dic2):
    row_values = [entry["Serial Number"], entry["Location"], entry["Test Station"], entry["Timestamp"]]
    row_values += [data_row[key] for key in head_keys]
    worksheet.append(row_values)

# Save the workbook to a file
workbook.save(o_filename)
print(f'Successfully wrote to {o_filename}')