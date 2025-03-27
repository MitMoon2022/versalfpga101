import json
import datetime
import os
import pandas as pd

# File date for the output Excel
filedate = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Directory containing JSON files
directory = './'                        #Create a Result folder and dump your data (json) file into it.
output_excel = f'./summary_Local_{filedate}.xlsx'

# Replace 'jobID' with the specific keywords you are looking for in the folder name
job_id_keyword = [
                  #'COMBO10_Versal2_VE3858_SSVA2112_XT50AV_202503191531',
                  #'COMBO10_Versal2_VE3858_SSVA2112_XT50AV_202503201203'
                  #'25March_55u'
                  'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202503211706',
                  'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202503241655'
                  ]

# List to store the structured data
data_masterlist = []
data_resultlist = []
data_testtimelist = []

# Function to extract relevant data from JSON files
def process_testTime(file_path, dataList):
    with open(file_path, 'r') as file:
        data = json.load(file)
        record = {}
        # Extract top-level information
        record = {
            'Date': data.get('Date', ''),
            'DNA': data.get('DNA', ''),
            'Temperature': data.get('Temperature', ''),
            'Voltage': data.get('Voltage', ''),
            'Site': data.get('siteNo', ''),
            'Program': data.get('Program', ''),
            'GitLabel': data.get('GitLabel', ''),
            'Total_Test_Time': data.get('Test_Time', data.get('TestTime', 0.0)),
            'OverHeadTestTime':0.0,
            'TotalIPTestTime':0.0,
            'Initialize_Time': data.get('Initialized_Time', data.get('Initialized_Time', 0.0)),
            'Temperature_Ramp_Start_Time': abs(data.get('TemperatureRampUpN120sSoakingTime', data.get('TemperatureRampUpN120sSoakingTime', 0.0))),
            'Temperature_Ramp_End_Time': abs(data.get('TemperatureRampUpN120sSoakingTimeEnd', data.get('TemperatureRampUpN120sSoakingTimeEnd', 0.0)))
        }

        #contact_check_runs = 0
        #record['contact_check_retest'] = contact_check_runs
        # Extract test results
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                test_name = test.get('Test_Name', '')
                #---insert----
                #if test_name in {'contact_check', 'CCHK_MC3', 'contact_check_LP5', 'contact_check_ddr5_DDR5_MC0'}:
                    #contact_check_runs += 1
                #---end-----
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            if test_name != '':
                                # testTime = float(test.get('Test_Time') or test.get('TestTime') or 0.0)
                                #record[f'{test_name}_testTime'] = float(testTime)
                                raw_test_time = test.get('Test_Time', test.get('TestTime', 0.0))
                                testTime = float(raw_test_time) if isinstance(raw_test_time, (int, float, str)) and str(raw_test_time).replace('.', '', 1).isdigit() else 0.0
                                record[f'{test_name}_testTime'] = float(testTime)
                                #totalIPTestTime += float(testTime)
                                
        #record['contact_check_retest'] = contact_check_runs
        dataList.append(record)

# Function to extract relevant data from JSON files
def process_value(file_path, dataList):
    with open(file_path, 'r') as file:
        data = json.load(file)
        record = {}
        # Extract top-level information
        record = {
            'Date': data.get('Date', ''),
            'Device': data.get('Device', ''),
            'DNA': data.get('DNA', ''),
            'Serial_Number': data.get('Serial_Number', ''),
            'Temperature': data.get('Temperature', ''),
            'Voltage': data.get('Voltage', ''),
            'Site': data.get('siteNo', ''),
            'Program': data.get('Program', ''),
            'GitLabel': data.get('GitLabel', ''),
        }

        # Extract test results
        contact_check_runs = 0
        record['contact_check_retest'] = contact_check_runs
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                test_name = test.get('Test_Name', '')
                #---insert----
                if test_name in {'contact_check', 'CCHK_MC3', 'contact_check_LP5', 'contact_check_ddr5_DDR5_MC0'}:
                    contact_check_runs += 1
                #---end-----
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            if test_name != '':
                                value = status.get('Value', None)
                                record[test_name] = value
                                if suite_name == "ALL_LPnom_R001":
                                    record[f'CC'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('CC', None)
                                    record[f'APU'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('APU', None)
                                    record[f'RPU'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('RPU', None)
                                    record[f'AIE'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('AIE', None)
                                    record[f'PCIE'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('PCIE', None)
                                    record[f'DDR'] = test.get('Results', {}).get('Status', {}).get('Detailed', {}).get('DDR', None)

        record['contact_check_retest'] = contact_check_runs
        dataList.append(record)

# Function to extract relevant data from JSON files
def processMasterJson(file_path, dataList):
    with open(file_path, 'r') as file:
        data = json.load(file)

        # Extract top-level information common to all rows
        common_record = {
            'DNA': data.get('DNA', ''),
            'Serial_Number': data.get('Serial_Number', ''),
            'Temperature': data.get('Temperature', ''),
            'Voltage': data.get('Voltage', ''),
            'Total_Test_Time': data.get('Test_Time', data.get('TestTime', 0.0)),
            'Initialize_Time': data.get('Initialized_Time', data.get('Initialized_Time', 0.0)),
            'Temperature_Ramp_Start_Time': data.get('TemperatureRampUpTime', data.get('TemperatureRampUpTime', 0.0)),
            'Temperature_Ramp_End_Time': data.get('TemperatureRampUpTimeEnd', data.get('TemperatureRampUpTimeEnd', 0.0)),
            'Block_Name': None,
            'Suite_Name': None,
            'Test_Name': None,
            'Value_Float': None,
            'Value_Pass_Fail': None,
            'Test_Time': None,
            'Project': data.get('Project', ''),
            'Device': data.get('Device', ''),
            'Package': data.get('Package', ''),
            'SiliconRev': data.get('SiliconRev', ''),
            'Date': data.get('Date', ''),
            'Time': data.get('Time', ''),
            'Site': data.get('siteNo', ''),
            'Program': data.get('Program', ''),
            'GitLabel': data.get('GitLabel', ''),
            'Log': data.get('Log', ''),
        }

        # Extract voltage information
        for key, value in data.items():
            if 'VCC' in key:
                common_record[key] = value

        # Extract test results and split into multiple rows
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            value = status.get('Value', None)

                            value_float = None
                            value_pass_fail = None
                            #value_string = None

                            # Create a new row for each test_name and value
                            row = common_record.copy()
                            row['Block_Name'] = block_name
                            row['Suite_Name'] = suite_name
                            row['Test_Name'] = test_name
                            row['Value_Float'] = value_float
                            row['Value_Pass_Fail'] = value_pass_fail
                            dataList.append(row)

                            # Add detailed results for specific suite_name if applicable
                            if suite_name == "ALL_LPnom_R001":
                                row['CC'] = status.get('Detailed', {}).get('CC', None)
                                row['APU'] = status.get('Detailed', {}).get('APU', None)
                                row['RPU'] = status.get('Detailed', {}).get('RPU', None)
                                row['AIE'] = status.get('Detailed', {}).get('AIE', None)
                                row['PCIE'] = status.get('Detailed', {}).get('PCIE', None)
                                row['DDR'] = status.get('Detailed', {}).get('DDR', None)

                else:
                    print(f"Warning: 'Test_Names' is not a dictionary in suite: {suite_name}")

def scan_directory(directory, job_id_keyword):
    if isinstance(job_id_keyword, str):
        job_id_keyword = [job_id_keyword]
    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory):
        if any(keyword in os.path.basename(root) for keyword in job_id_keyword):
            json_files = [f for f in files if f.endswith('.json')]
            if json_files:
                for json_file in json_files:
                    print(f'Processing JSON = {os.path.join(root, json_file)}')
                    processMasterJson(os.path.join(root, json_file), data_masterlist)
                    process_value(os.path.join(root, json_file), data_resultlist)
                    process_testTime(os.path.join(root, json_file), data_testtimelist)
                    print(f'Processed JSON = {os.path.join(root, json_file)}')

scan_directory(directory, job_id_keyword)

# Create a DataFrame and save to Excel
# Create DataFrames for each tab
df_tab1 = pd.DataFrame(data_masterlist)
df_tab2 = pd.DataFrame(data_resultlist)
df_tab3 = pd.DataFrame(data_testtimelist)
# Save the DataFrames into an Excel file with multiple sheets
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    df_tab1.to_excel(writer, sheet_name='Master_Summary', index=False)  #Leave it
    #df_tab2.to_excel(writer, sheet_name='Result_Summary', index=False)
    #df_tab3.to_excel(writer, sheet_name='TestTime_Summary', index=False)   #Leave it

print(f"Excel file generated with multiple tabs: {output_excel}")
