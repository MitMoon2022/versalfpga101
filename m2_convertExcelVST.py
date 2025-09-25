import json
import re
import datetime
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Force Matplotlib to use a non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import argparse
import os

# File date for the output Excel
filedate = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

excepted_lower_margin = 0.985
excepted_higher_margin = 1.015

#Hardcode for Telluride:
LPMin =  [0.676, 0.676]
MPMin =  [0.760, 0.760]
MHPMin = [0.760, 0.836]
MHPMax = [0.840, 0.924]
LHPMin = [0.676, 0.836]
LHPNom = [0.700, 0.880]
LXHP = [0.700, 0.880]

# Directory containing JSON files
#binning = "./Binning.json"
#directory = './../Result/'
binning = "./PostProcess/Binning.json"
directory = '/group/xap_charserv2/engineering/Characterization/charmnt/Robot-SLT/XAP/Python_Automation_Framework/SLTRobot_Python_Automation'
#'/group/xap_charserv2/engineering/Characterization/charmnt/Robot-SLT/XAP/Robot_PythonAutomation/SLT04/SLTRobot_Python_Automation'


# Replace 'jobID' with the specific keywords you are looking for in the folder name
job_id_keyword = []

#output_excel = f'./../FinalResult/Telluride/VST/T20/batch14_vid_overall_summary_start.xlsx'
#Argument parser setup
parser = argparse.ArgumentParser(
    description="""Generate Excel summary for a specific job ID.
Example:
    python3.12 m2_convertExcelVST.py \
COMBO10_Versal2_VE3558_SSVA2112_XT20AV_202508250930_B18r \
T20 B18-summary_restest.xlsx
"""
)

parser.add_argument('job_id_keyword', type=str, help='Keyword to identify job ID (e.g., folder name)')
parser.add_argument('platform', type=str, choices=['T20', 'T50'], help='Platform type (T20 or T50)')
parser.add_argument('output_filename', type=str, help='Excel output filename (e.g., summary_start.xlsx)')

args = parser.parse_args()

# Ensure output filename ends with .xlsx
filename = args.output_filename
if not filename.lower().endswith('.xlsx'):
    filename += '.xlsx'

print(f"Output Filename: {repr(filename)}")

# Variables
job_id_keyword = [args.job_id_keyword]
output_excel = f'./FinalResult/Telluride/VST/{args.platform}/{filename}'

# Optional debug output
print(f"Job ID Keyword: {job_id_keyword}")
print(f"Output Excel Path: {output_excel}")

os.makedirs(os.path.dirname(output_excel), exist_ok=True)

# List to store the structured data
data_masterlist = []
data_resultlist = []
data_testtimelist = []
data_resultbinninglist = []

def safe_float(test_dict, keys, default=0.0):
    """
    Convert the first found valid key in keys to float.
    If no valid key is found, return default.
    """
    for key in keys:
        if key in test_dict:
            value = test_dict[key]
            # print(f"Found key: {key} -> Value: {value}")  # Debugging Output
            if isinstance(value, (int, float)):  # If already a number
                return float(value)
            elif isinstance(value, str) and value.replace('.', '', 1).isdigit():  # If valid float string
                return float(value)
    # print(f"No valid keys found in {keys}, returning default {default}")  # Debugging Output
    return default  # Default if no valid key is found


# Function to extract relevant data from JSON files
def process_binning(file_path):
    with open(file_path, 'r') as file:
        data_binning = json.load(file)

    return data_binning

# Process the JSON file
data_binning = process_binning(binning)

# Check the output
# print(data_binning)  # Now this should show the JSON content

# Function to extract relevant data from JSON files
def process_testTime(file_path, dataList):
    with open(file_path, 'r') as file:
        data = json.load(file)
        record = {}
        # Extract top-level information
        record = {
            'Device': data.get('Device', ''),
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

        # Define voltage reference dictionary
        tempDict = {
            'LPMin':  [0.676, 0.676],
            'MPMin':  [0.760, 0.760],
            'MHPMin': [0.760, 0.836],
            'MHPMax': [0.840, 0.924],
            'LHPMin': [0.676, 0.836],
            'LHPNom': [0.700, 0.880],
            'LXHP': [0.700, 0.880],
        }

        comparingdict = {}
        # Extract voltage information with 1% tolerance check
        for key, value in data.items():
            if 'VCC' in key:
                comparingdict[key] = float(value)  # Store the VCC value in common_record

                if 'VCC_INT' in key:
                    expected_value = tempDict[record['Voltage']][0]
                    # print(f'expected value = {expected_value}, value = {float(value)}')
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        record['Voltage'] = 'InvalidVoltage'
                        break

                if 'VCC_LPD' in key:
                    expected_value = tempDict[record['Voltage']][1]
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        record['Voltage'] = 'InvalidVoltage'
                        break

        contact_check_runs = 0
        totalIPTestTime = 0.0
        prevTestTime = 0.0000
        #Hardcode for ASU
        ASUoverheadTime = 0.0
        # Extract test results
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                test_name = test.get('Test_Name', '')
                # Hard code for telluride purpose
                if "t20_aie2ps" in test_name:
                    test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)
                elif "t20_run_aie2ps" in test_name:
                    test_name = test_name.replace("t20_run_aie2ps", "aie2ps", 1)
                elif "run_aie2ps" in test_name:
                    test_name = test_name.replace("run_aie2ps", "aie2ps", 1)

                if test_name in {'contact_check', 'CCHK_MC3', 'contact_check_LP5', 'contact_check_ddr5_DDR5_MC0'}:
                    contact_check_runs += 1
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    if "t20_aie2ps" in test_name:
                        test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)
                    elif "t20_run_aie2ps" in test_name:
                        test_name = test_name.replace("t20_run_aie2ps", "aie2ps", 1)
                    elif "run_aie2ps" in test_name:
                        test_name = test_name.replace("run_aie2ps", "aie2ps", 1)
                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            if test_name != '':
                                # testTime = float(test.get('Test_Time') or test.get('TestTime') or 0.0)
                                raw_test_time = test.get('Test_Time', test.get('TestTime', 0.0))
                                testTime = float(raw_test_time) if isinstance(raw_test_time, (int, float, str)) and str(raw_test_time).replace('.', '', 1).isdigit() else 0.0
                                deltawithprev = prevTestTime - testTime
                                prevTestTime = testTime
                                if deltawithprev == 0.00000:
                                    testTime = 0.0
                                if record.get(f'{test_name}_testTime'):
                                    record[f'{test_name}_{contact_check_runs}_testTime'] = float(testTime)
                                    totalIPTestTime += float(testTime)
                                else:
                                    record[f'{test_name}_testTime'] = float(testTime)
                                    totalIPTestTime += float(testTime)

                                if test_name == 'ASU_FMAX' or test_name == 'ASU_PL_FMAX':
                                    raw_test_time = test.get('LoadModule_Time', test.get('LoadModule_Time', 0.0))
                                    testTime = float(raw_test_time) if isinstance(raw_test_time, (int, float, str)) and str(raw_test_time).replace('.', '', 1).isdigit() else 0.0
                                    ASUoverheadTime += testTime
                        else:
                            # testTime = float(test.get('Test_Time') or test.get('TestTime') or 0.0)
                            raw_test_time = test.get('Test_Time', test.get('TestTime', 0.0))
                            testTime = float(raw_test_time) if isinstance(raw_test_time, (int, float, str)) and str(raw_test_time).replace('.', '', 1).isdigit() else 0.0
                            record[f'{test_name}_testTime'] = float(testTime)
                            totalIPTestTime += float(testTime)

        record['OverHeadTestTime'] = data.get('Test_Time', data.get('TestTime', 0.0)) - totalIPTestTime + ASUoverheadTime
        record['TotalIPTestTime'] =  totalIPTestTime
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

        # Define voltage reference dictionary
        tempDict = {
            'LPMin':  [0.676, 0.676],
            'MPMin':  [0.760, 0.760],
            'MHPMin': [0.760, 0.836],
            'MHPMax': [0.840, 0.924],
            'LHPMin': [0.676, 0.836],
            'LHPNom': [0.700, 0.880],
            'LXHP': [0.700, 0.880],
        }

        comparingdict = {}
        # Extract voltage information with 1% tolerance check
        for key, value in data.items():
            if 'VCC' in key:
                comparingdict[key] = float(value)  # Store the VCC value in common_record

                if 'VCC_INT' in key:
                    expected_value = tempDict[record['Voltage']][0]
                    # print(f'expected value = {expected_value}, value = {float(value)}')
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        record['Voltage'] = 'InvalidVoltage'
                        break

                if 'VCC_LPD' in key:
                    expected_value = tempDict[record['Voltage']][1]
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        record['Voltage'] = 'InvalidVoltage'
                        break

        contact_check_runs = 0
        record['contact_check_retest'] = contact_check_runs
        # Extract test results
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                test_name = test.get('Test_Name', '')
                if 't20_aie2ps' in test_name:
                    test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)

                elif 'run_aie2ps' in test_name:
                    test_name = test_name.replace("run_aie2ps", "aie2ps", 1)

                if test_name in {'contact_check', 'CCHK_MC3', 'contact_check_LP5', 'contact_check_ddr5_DDR5_MC0'}:
                    contact_check_runs += 1

                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    if "t20_aie2ps" in test_name:
                        test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)
                    elif "t20_run_aie2ps" in test_name:
                        test_name = test_name.replace("t20_run_aie2ps", "aie2ps", 1)
                    elif "run_aie2ps" in test_name:
                        test_name = test_name.replace("run_aie2ps", "aie2ps", 1)
                    if "_LOG" in test_name or "_MSG" in test_name:
                        continue
                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            if test_name != '':
                                value_float = None
                                value_pass_fail = None
                                value_string = None
                                if isinstance(value, (int, float)):  # Check if value is int or float
                                    value_float = float(value)
                                    value = float(value)
                                elif isinstance(value, str):  # Check if value is a string
                                    value = value.strip()
                                    if value.replace('.', '', 1).isdigit():  # Check if it's a numeric string
                                        value_float = float(value)
                                        value = float(value)
                                    elif value.upper() in {"PASS", "FAIL", "Pass", "Fail"}:  # Check if it's "PASS" or "FAIL"
                                        value_pass_fail = value.upper()
                                        value = value.upper()
                                    else:
                                        value_string = value  # Assign other strings here
                                else:
                                    value_string = str(value)  # Convert other types to string

                                value = status.get("Value")

                                if value is None:
                                    if "Vhole" in status and isinstance(status["Vhole"], list) and len(status["Vhole"]) > 1:
                                        value = f'VHole ({status["Vhole"][1]})'  # Format as 'VHole (value)'
                                    elif "Vmin" in status:
                                        value = status["Vmin"]
                                    else:
                                        value = None  # Default fallback

                                if record.get(test_name):
                                    record[f'{test_name}_{contact_check_runs}'] = value
                                else:
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

def process_value_binning(file_path, dataList, binning_data):
    with open(file_path, 'r') as file:
        data = json.load(file)
        common_record = {}
        # Extract top-level information
        common_record = {
            'Date': data.get('Date', ''),
            'Device': data.get('Device', ''),
            'DNA': data.get('DNA', ''),
            'Serial_Number': data.get('Serial_Number', ''),
            'Temperature': data.get('Temperature', ''),
            'Voltage': data.get('Voltage', ''),
            'GitLabel': data.get('GitLabel', ''),
        }

        # Define voltage reference dictionary
        tempDict = {
            'LPMin':  [0.676, 0.676],
            'MPMin':  [0.760, 0.760],
            'MHPMin': [0.760, 0.836],
            'MHPMax': [0.840, 0.924],
            'LHPMin': [0.676, 0.836],
            'LHPNom': [0.700, 0.880],
            'LXHP': [0.700, 0.880],
        }

        comparingdict = {}
        # Extract voltage information with 1% tolerance check
        for key, value in data.items():
            if 'VCC' in key:
                comparingdict[key] = float(value)  # Store the VCC value in common_record

                if 'VCC_INT' in key:
                    expected_value = tempDict[common_record['Voltage']][0]
                    # print(f'expected value = {expected_value}, value = {float(value)}')
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        common_record['Voltage'] = 'InvalidVoltage'
                        break

                if 'VCC_LPD' in key:
                    expected_value = tempDict[common_record['Voltage']][1]
                    if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                        # print('do nothing')
                        pass
                    else:
                        common_record['Voltage'] = 'InvalidVoltage'
                        break

        def flatten_dict(data, row, parent_key=""):
            for key, item in data.items():
                new_key = f"{parent_key}_{key}" if parent_key else key  # Create a unique key path

                if isinstance(item, dict):  # If item is a nested dictionary, recurse
                    flatten_dict(item, row, new_key)
                else:
                    row[new_key] = item  # Store values with unique key names

        contact_check_runs = 0
        # Extract test results and split into multiple rows
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')

                    if "t20_aie2ps" in test_name:
                        test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)
                    elif "t20_run_aie2ps" in test_name:
                        test_name = test_name.replace("t20_run_aie2ps", "aie2ps", 1)
                    elif "run_aie2ps" in test_name:
                        test_name = test_name.replace("run_aie2ps", "aie2ps", 1)


                    if test_name in {'contact_check', 'CCHK_MC3', 'contact_check_LP5', 'contact_check_ddr5_DDR5_MC0'}:
                        contact_check_runs += 1

                    if "_LOG" in test_name or "_MSG" in test_name:
                        continue

                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            value = status.get("Value")

                            if value is None:
                                if "Vhole" in status and isinstance(status["Vhole"], list) and len(status["Vhole"]) > 1:
                                    value = f'VHole ({status["Vhole"][1]})'  # Format as 'VHole (value)'
                                elif "Vmin" in status:
                                    value = status["Vmin"]
                                else:
                                    value = None  # Default fallback


                            value_float = None
                            value_pass_fail = None
                            value_string = None
                            if isinstance(value, (int, float)):  # Check if value is int or float
                                value_float = float(value)
                            elif isinstance(value, str):  # Check if value is a string
                                value = value.strip()
                                if value.replace('.', '', 1).isdigit():  # Check if it's a numeric string
                                    value_float = float(value)
                                elif value.upper() in {"PASS", "FAIL", "Pass", "Fail"}:  # Check if it's "PASS" or "FAIL"
                                    value_pass_fail = value.upper()
                                else:
                                    value_string = value  # Assign other strings here
                            else:
                                value_string = str(value)  # Convert other types to string


                            row = common_record.copy()
                            row['Value_Float'] = value_float
                            row['Value_Pass_Fail'] = value_pass_fail
                            row['Value_String'] = value_string
                            row['Suite_Name'] = suite_name
                            row['Test_Name'] = test_name
                            row['Value'] = value
                            # dataList.append(row)
                            # Example usage
                            if common_record['DNA'] in binning_data:
                                dna = common_record['DNA']
                                binning = binning_data[dna]
                                sn = binning['sn']
                                print(sn)
                                # if not sn:
                                #     print(f'serial number not found')
                                #     sn = common_record['Serial_Number']
                                #     print(sn)
                                #     keys = [k for k, v in binning_data.items() if v.get("sn") == sn]
                                #     print(keys, sn)  # Output: XV42GWLTQ0VM9OW7
                                #     binning['sn'] = binning_data[keys[0]]['sn']
                                #     binning['Comment'] = 'MismatchSnWithSharepoint'
                                #     binning['Corner'] = binning_data[keys[0]]['Corner']
                                #     binning['LVT_detail'] = binning_data[keys[0]]['LVT_detail']
                                #     binning['SVT_detail'] = binning_data[keys[0]]['SVT_detail']
                                #     binning['ULVT_detail'] = binning_data[keys[0]]['ULVT_detail']

                                if isinstance(binning, dict):
                                    flatten_dict(binning, row)
                                else:
                                    print(f"Warning: binning_data[{dna}] is not a dictionary. Value: {binning}")

                            dataList.append(row)
                else:
                    print(f"Warning: 'Test_Names' is not a dictionary in suite: {suite_name}")

# Function to extract relevant data from JSON files
def processMasterJson(file_path, dataList):
    with open(file_path, 'r') as file:
        data = json.load(file)
        common_record = {}
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

        # Define voltage reference dictionary
        tempDict = {
            'LPMin':  [0.676, 0.676],
            'MPMin':  [0.760, 0.760],
            'MHPMin': [0.760, 0.836],
            'MHPMax': [0.840, 0.924],
            'LHPMin': [0.676, 0.836],
            'LHPNom': [0.700, 0.880],
            'LXHP': [0.700, 0.880],
        }

        checkVoltageCorrect = 0
        # Extract voltage information with 1% tolerance check
        for key, value in data.items():
            if 'VCC' in key:
                common_record[key] = float(value)  # Store the VCC value in common_record

                if checkVoltageCorrect == 0:
                    if 'VCC_INT' in key:
                        expected_value = tempDict[common_record['Voltage']][0]
                        # print(f'expected value = {expected_value}, value = {float(value)}')
                        if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                            print('do nothing')
                        else:
                            common_record['Voltage'] = 'InvalidVoltage'
                            checkVoltageCorrect = 1

                    if 'VCC_LPD' in key:
                        expected_value = tempDict[common_record['Voltage']][1]
                        if expected_value * excepted_lower_margin <= float(value) <= expected_value * excepted_higher_margin:
                            print('do nothing')
                        else:
                            common_record['Voltage'] = 'InvalidVoltage'
                            checkVoltageCorrect = 1

        # Extract test results and split into multiple rows
        for block in data.get('Blocks', []):
            block_name = block.get('Name', '')
            for suite in block.get('Test_Suites', []):
                suite_name = suite.get('Suite_Name', '')
                test = suite.get('Test_Names', {})
                if isinstance(test, dict):  # Ensure 'Test_Names' is a dictionary
                    test_name = test.get('Test_Name', '')
                    if "t20_aie2ps" in test_name:
                        test_name = test_name.replace("t20_aie2ps", "aie2ps", 1)
                    elif "t20_run_aie2ps" in test_name:
                        test_name = test_name.replace("t20_run_aie2ps", "aie2ps", 1)
                    elif "run_aie2ps" in test_name:
                        test_name = test_name.replace("run_aie2ps", "aie2ps", 1)

                    # Keys to process
                    # Define possible keys with variations
                    key_variants = {
                        'sysmonTempMin':  ['Temperature_Min', 'Tmperature_Min'],
                        'sysmonTempMax':  ['Temperature_Max', 'Tmperature_Max'],
                        'sysmonVccInt':   ['VCC_INT', 'Vcc_Int'],
                        'sysmonVccLpd':   ['VCC_LPD', 'Vcc_Lpd'],
                        'sysmonVccFpd':   ['VCC_FPD', 'Vcc_Fpd'],
                        'sysmonVccIoSoc': ['VCC_IO_SOC', 'Vcc_Io_Soc'],
                        'sysmonRam':      ['VCC_RAM', 'Vcc_Ram'],
                        'sysmonPmc':      ['VCC_PMC', 'Vcc_Pmc'],
                        'sysmonAie':      ['VCC_AIE', 'Vcc_Aie']
                    }

                    # Process and assign values dynamically
                    sysmonTempMin, sysmonTempMax, sysmonVccInt, sysmonVccLpd, sysmonVccFpd, \
                    sysmonVccIoSoc, sysmonRam, sysmonPmc, sysmonAie = (
                        safe_float(test, key_variants[var]) for var in key_variants
                    )

                    results = test.get('Results', {})
                    if isinstance(results, dict):  # Ensure 'Results' is a dictionary
                        status = results.get('Status', {})
                        if isinstance(status, dict):  # Ensure 'Status' is a dictionary
                            value = status.get("Value")

                            if value is None:
                                if "Vhole" in status and isinstance(status["Vhole"], list) and len(status["Vhole"]) > 1:
                                    value = f'VHole ({status["Vhole"][1]})'  # Format as 'VHole (value)'
                                elif "Vmin" in status:
                                    value = status["Vmin"]
                                else:
                                    value = None  # Default fallback

                            value_float = None
                            value_pass_fail = None
                            value_string = None
                            if isinstance(value, (int, float)):  # Check if value is int or float
                                value_float = float(value)
                            elif isinstance(value, str):  # Check if value is a string
                                value = value.strip()
                                if value.replace('.', '', 1).isdigit():  # Check if it's a numeric string
                                    value_float = float(value)
                                elif value.upper() in {"PASS", "FAIL", "Pass", "Fail"}:  # Check if it's "PASS" or "FAIL"
                                    value_pass_fail = value.upper()
                                else:
                                    value_string = value  # Assign other strings here
                            else:
                                value_string = str(value)  # Convert other types to string

                            # Create a new row for each test_name and value
                            row = common_record.copy()
                            row['Block_Name'] = block_name
                            row['Suite_Name'] = suite_name
                            row['Test_Name'] = test_name
                            row['Value_Float'] = value_float
                            row['Value_Pass_Fail'] = value_pass_fail
                            row['Value_String'] = value_string
                            row['Test_Time'] = float(test.get('Test_Time') or test.get('TestTime') or 0.0)
                            row['sysmonTempMin'] = sysmonTempMin
                            row['sysmonTempMax'] = sysmonTempMax
                            row['sysmonVccInt'] = sysmonVccInt
                            row['sysmonVccLpd'] = sysmonVccLpd
                            row['sysmonVccFpd'] = sysmonVccFpd
                            row['sysmonVccIoSoc'] = sysmonVccIoSoc
                            row['sysmonRam'] = sysmonRam
                            row['sysmonPmc'] = sysmonPmc
                            row['sysmonAie'] = sysmonAie
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
                    process_value_binning(os.path.join(root, json_file), data_resultbinninglist, data_binning)
                    print(f'Processed JSON = {os.path.join(root, json_file)}')

scan_directory(directory, job_id_keyword)

# Create a DataFrame and save to Excel
# Create DataFrames for each tab
df_tab1 = pd.DataFrame(data_masterlist)
df_tab2 = pd.DataFrame(data_resultlist)
df_tab3 = pd.DataFrame(data_testtimelist)
df_tab4 = pd.DataFrame(data_resultbinninglist)
# # Save the DataFrames into an Excel file with multiple sheets
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    df_tab1.to_excel(writer, sheet_name='Master_Summary', index=False)
    df_tab2.to_excel(writer, sheet_name='Result_Summary', index=False)
    df_tab3.to_excel(writer, sheet_name='TestTime_Summary', index=False)
    df_tab4.to_excel(writer, sheet_name='Result_Binning_Summary', index=False)

print(f"Excel file generated with multiple tabs: {output_excel}")


