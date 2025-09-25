import json
import datetime
import os
import pandas as pd
import xlsxwriter.utility  # To safely handle column names beyond Z

# File date for the output Excel
filedate = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Directory containing JSON files
directory = './'                        #Create a Result folder and dump your data (json) file into it.
output_excel = f'./summary_Local_{filedate}.xlsx'

# Replace 'jobID' with the specific keywords you are looking for in the folder name
job_id_keyword = [
                  #'run3'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508011334'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508081120'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508181352'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508181507'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508181555'
                  #'cck'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508220930'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508271012'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202509051358'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202509051358',
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202509081400_B19r'
                  #'COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202509121004'  #retest
                  'debug_mm1'
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

# Function to extract relevant data from JSON files -for resultlist
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
            'Log': data.get('Log', ''),
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
                                # Remove leading/trailing spaces if value is a string
                                if isinstance(value, str):
                                    value = value.strip()  # Trim spaces
                                # Check if value is a string and matches 'pass' or 'fail' (case-insensitive)
                                if isinstance(value, str) and value.lower() in ['pass', 'fail']:
                                    record[test_name] = value.lower()  # Store as 'pass' or 'fail'
                                # Skip if the value is a float
                                elif isinstance(value, float):
                                    continue  # Skip this iteration and do not save the value

        # Remove any entries where the value is None or an empty string
        record = {key: value for key, value in record.items() if value not in [None, '']}        
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
                    #print(f'Processing JSON = {os.path.join(root, json_file)}')
                    processMasterJson(os.path.join(root, json_file), data_masterlist)
                    process_value(os.path.join(root, json_file), data_resultlist)
                    process_testTime(os.path.join(root, json_file), data_testtimelist)
                    #print(f'Processed JSON = {os.path.join(root, json_file)}')

scan_directory(directory, job_id_keyword)

# Create a DataFrame and save to Excel
# Create DataFrames for each tab
df_tab1 = pd.DataFrame(data_masterlist)
df_tab2 = pd.DataFrame(data_resultlist)
df_tab3 = pd.DataFrame(data_testtimelist)
# Save the DataFrames into an Excel file with multiple sheets
# Modify start here:
# Define the columns to evaluate (starting from 'contact_check_lp5_LP5_MC3' to 'RPUBURST_VST')
test_columns = df_tab2.columns.tolist()

try:
    start_index = test_columns.index('contact_check_lp5_LP5_MC3')
except ValueError as e:
    raise RuntimeError("'contact_check_lp5_LP5_MC3' not found in DataFrame columns.") from e

try:
    end_index = test_columns.index('VCU_ENC_AVC_HIGH_RES')
except ValueError:
    # Use the last column if the end column is not found
    end_index = len(test_columns) - 1

# Define the test evaluation columns
test_eval_columns = test_columns[start_index:end_index+1]
#-------------------------------------------------------------------------------------------
#Tag these "all-blank" failures differently, return 'fail' if any test cell contains 'fail'
# def evaluate_remark(row):
#     # Extract non-blank test results
#     non_blank = [str(val).strip().lower() for val in row if pd.notna(val) and str(val).strip() != '']
    
#     if not non_blank:
#         return 'fail(blank)'
#     elif 'fail' in non_blank:
#         return 'fail'
#     else:
#         return 'pass'

# Improved evaluate_remark function with additional condition
def evaluate_remark(row):
    # Extract non-blank test results
    non_blank = [str(val).strip().lower() for val in row if pd.notna(val) and str(val).strip() != '']
    
    if not non_blank:
        return 'fail(blank)'
    
    # Count occurrences of 'pass' and other relevant results
    pass_count = non_blank.count('pass')
    fail_count = non_blank.count('fail')
    
    #print(f"Pass = ",pass_count)
    #print(f"fail = ",fail_count)
    
    if fail_count > 0:
        return 'fail'
    elif pass_count <= 2:  # Check condition for 1 or 2 passes
        # You can return 'warning' directly here
        return 'warning'
    else:
        return 'pass'  # If there are more than 2 passes, return 'pass'
    
   

df_tab2['remark'] = df_tab2[test_eval_columns].apply(evaluate_remark, axis=1)
#-----------------------------------------------------------------------------------
#Add
# Define the columns to evaluate
# test_columns = df_tab2.columns.tolist()
# start_index = test_columns.index('contact_check_lp5_LP5_MC3')
# end_index = test_columns.index('RPUBURST_VST')
# test_eval_columns = test_columns[start_index:end_index + 1]

# Generate 'Reason' column: list of test names with value 'fail'
def collect_fail_reasons(row):
    failed_tests = [col for col in test_eval_columns if str(row.get(col, '')).strip().lower() == 'fail']
    return ', '.join(failed_tests) if failed_tests else ''

df_tab2['Reason'] = df_tab2.apply(collect_fail_reasons, axis=1)

# Convert 'Date' column to datetime if not already
df_tab2['Date'] = pd.to_datetime(df_tab2['Date'], errors='coerce')

# Sort by Date ascending
df_tab2 = df_tab2.sort_values(by='Date', ascending=True).reset_index(drop=True)

# Count occurrences of each Serial_Number
df_tab2['TestCount'] = df_tab2['Serial_Number'].map(df_tab2['Serial_Number'].value_counts())
# add a column to track the test count with label 'p' or 'f'
def assign_checkF(row):
    tc = row['TestCount']
    remark = str(row['remark']).strip().lower()
    
    if tc >= 2:
        if remark == 'pass':
            return f'P{tc}'
        else:
            return f'F{tc}'
    return ''

df_tab2['checkF'] = df_tab2.apply(assign_checkF, axis=1)

# Identify Serial_Numbers with NO 'pass' in any remark
no_pass_serials = df_tab2.groupby('Serial_Number')['remark'].apply(lambda remarks: 'pass' not in remarks.str.lower().values)

# Map result to FailCheck column — 'TIC' or 'TestComplete'
df_tab2['FailCheck'] = df_tab2['Serial_Number'].map(
    lambda sn: 'FailingUnit' if no_pass_serials.get(sn, False) else 'TestComplete'
)

# Step 1: Filter only rows with FailCheck == 'TIC'
tic_rows = df_tab2[df_tab2['FailCheck'] == 'FailingUnit'].copy()

# Step 2: For each Serial_Number, keep the row with the highest TestCount
tic_filtered = tic_rows.sort_values(['Serial_Number', 'TestCount'], ascending=[True, False])
tic_unique = tic_filtered.drop_duplicates(subset='Serial_Number', keep='first')
#//===============================================================================
# Create the 'overall' tab
# Start with unique Serial_Number rows initialized to 'fail' or blank
# Create the 'overall' tab
overall_df = pd.DataFrame(columns=['Serial_Number', 'Log'] + test_eval_columns)

# Group rows by Serial_Number
for sn, group in df_tab2.groupby('Serial_Number'):
    overall_row = {'Serial_Number': sn}

    # Join all unique logs (comma separated)
    logs = group['Log'].dropna().astype(str).unique()
    overall_row['Log'] = ', '.join(logs) if len(logs) > 0 else ''

    for col in test_eval_columns:
        values = group[col].dropna().astype(str).str.lower().str.strip()
        if 'pass' in values.values:
            overall_row[col] = 'pass'
        elif 'fail' in values.values:
            overall_row[col] = 'fail'
        else:
            overall_row[col] = ''

    overall_df = pd.concat([overall_df, pd.DataFrame([overall_row])], ignore_index=True)

overall_df['remark'] = overall_df[test_eval_columns].apply(evaluate_remark, axis=1)

# --- Add Pcount & Fcount for remark column ---
pcount_total = (overall_df['remark'].str.lower() == 'pass').sum()
fcount_total = overall_df['remark'].str.lower().str.startswith('fail').sum()

#print(pcount_total)

# Put the same totals in every row (optional: could also keep them separate)
overall_df['PASS'] = ''                       #change name from Pcount
overall_df['FAIL'] = ''                       #change name from Fcount

#overall_df['Log'] = df_tab2['log']
#'Log': data.get('Log', '')

#//===============================================================================
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    df_tab2.to_excel(writer, sheet_name='Result_Summary', index=False)
    df_tab3.to_excel(writer, sheet_name='TestTime_Summary', index=False)
    # Write to new sheet 'TIC_Units'
    tic_unique.to_excel(writer, sheet_name='FailingUnits', index=False)
    overall_df.to_excel(writer, sheet_name='Overall', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Result_Summary']

    # Create formats for 'pass' and 'fail'
    format_pass = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})  # Light green fill, dark green text
    format_fail = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})  # Light red fill, dark red text
    
    # Define formats
    green_fill = workbook.add_format({'bg_color': "#32C4BF", 'font_color': "#110BBF"})  # Green fill, dark blue text

    # Get column indexes for the defined test range
    test_columns = df_tab2.columns.tolist()
    #start_index = test_columns.index('contact_check_lp5_LP5_MC3')
    #end_index = test_columns.index('RPUBURST_VST')
    
    try:
        start_index = test_columns.index('contact_check_lp5_LP5_MC3')
    except ValueError as e:
        raise RuntimeError("'contact_check_lp5_LP5_MC4' not found in DataFrame columns.") from e

    try:
        end_index = test_columns.index('VCU_ENC_AVC_HIGH_RES')
    except ValueError:
        end_index = len(test_columns) - 1  # Use the last column if end column not found
    
    num_rows = len(df_tab2) + 1  # include header row

    # Loop through each column in the range and apply conditional formatting
    for col_idx in range(start_index, end_index + 1):
        col_letter = xlsxwriter.utility.xl_col_to_name(col_idx)
        cell_range = f'{col_letter}2:{col_letter}{num_rows}'

        # Apply 'pass' formatting
        worksheet.conditional_format(cell_range, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'pass',
            'format': format_pass
        })

        # Apply 'fail' formatting
        worksheet.conditional_format(cell_range, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'fail',
            'format': format_fail
        })

    # Optionally, also format the 'remark' column itself
    if 'remark' in df_tab2.columns:
        remark_col_idx = df_tab2.columns.get_loc('remark')
        remark_col_letter = xlsxwriter.utility.xl_col_to_name(remark_col_idx)
        cell_range = f'{remark_col_letter}2:{remark_col_letter}{num_rows}'

        worksheet.conditional_format(cell_range, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'pass',
            'format': format_pass
        })
        worksheet.conditional_format(cell_range, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'fail',
            'format': format_fail
        })
    for sheet_name in ['Result_Summary', 'FailingUnits']:
        worksheet = writer.sheets[sheet_name]
        df = df_tab2 if sheet_name == 'Result_Summary' else tic_unique

        # Find column indexes
        headers = df.columns.tolist()
        tc_col = headers.index('TestCount')
        fc_col = headers.index('FailCheck')

        # Apply formatting on 'TestCount' == 1
        worksheet.conditional_format(1, tc_col, len(df), tc_col, {
            'type':     'cell',
            'criteria': '==',
            'value':    1,
            'format':   green_fill
        })

        # Apply formatting on 'FailCheck' == 'TestComplete'
        worksheet.conditional_format(1, fc_col, len(df), fc_col, {
            'type':     'text',
            'criteria': 'containing',
            'value':    'TestComplete',
            'format':   green_fill
        })
# # === Add 'failunits' Sheet ===
#     df_failunits = df_tab2[df_tab2['remark'] == 'fail']
#     df_failunits.to_excel(writer, sheet_name='failunits', index=False)

# Access the 'Overall' worksheet
    ws = writer.sheets['Overall']

    # Get column indexes for Pcount and Fcount
    pcount_col_idx = overall_df.columns.get_loc('PASS')
    fcount_col_idx = overall_df.columns.get_loc('FAIL')

    # Write the totals into row 2 (below header row)
    ws.write(1, pcount_col_idx, pcount_total)  # row 1 in 0-based index = Excel row 2
    ws.write(1, fcount_col_idx, fcount_total)

print(f"Excel file generated with multiple tabs: {output_excel}")
