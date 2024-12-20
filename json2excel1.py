
import json
import os
import csv
import re
import time
import pandas as pd
from datetime import datetime   #for timestamp usage

# A script to extract Specific Headers and Values

def json_to_excel(json_file, excel_file, headers_to_extract):
    # Read the JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Function to extract specific headers
    def extract_headers(data, headers):
        extracted_data = {}
        for header in headers:
            keys = header.split('.')
            value = data
            for key in keys:
                if key in value:
                    value = value[key]
                else:
                    value = None
                    break
            extracted_data[header] = value
        return extracted_data

    # Extract headers from the JSON data
    extracted_data = extract_headers(data, headers_to_extract)

    # Convert the extracted data to a DataFrame
    df = pd.DataFrame([extracted_data])
    
    # Save DataFrame to Excel file
    df.to_excel(excel_file, index=False)

# Example usage
cwd = os.getcwd()
print("--->",cwd)
json_file = 'data1.json'  # Path to your JSON file
excel_file = 'data1.xlsx'  # Desired path for the Excel file
headers_to_extract = ['RobotL.Enable', 'RobotL.Type', 'RobotL.Controller', 'RobotL.Terminal.PythonBash']  # Headers to extract
json_to_excel(json_file, excel_file,headers_to_extract)

print(f'Successfully wrote to {excel_file}')
