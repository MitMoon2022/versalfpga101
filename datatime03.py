import subprocess
import re
import csv
from datetime import datetime

# Run the 'dir /OD' command and capture its output
output = subprocess.check_output(['cmd', '/C', 'dir', '/OD']).decode('utf-8')

print(output)

# Regular expression pattern to extract date-time and filename
#pattern = r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[AP]M)\s+\d+\s+(snX\w+_m40_result\.txt)"
pattern = r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[AP]M)\s+\d+\s+sn(X\w{16})_m40_result\.txt"


# Find all matches in the directory listing
matches = re.findall(pattern, output)

# Print the matches
for match in matches:
    print("Filename:", match[1])
    print("Date-Time:", match[0])
    print()



'''

# Define a regular expression pattern to match datetime strings in the directory listing
datetime_pattern = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2} [AP]M')

# Function to extract datetime information from the directory listing output
def extract_datetime_from_dir_output(output):
    datetime_list = []
    for line in output.split('\n'):
        matches = re.findall(datetime_pattern, line)
        if matches:
            datetime_list.extend(matches)
    return datetime_list

# Example usage
datetimes = extract_datetime_from_dir_output(output)

# Print the extracted datetime strings
print("Extracted datetime strings:")
print(datetimes)

# Convert datetime strings to datetime objects
datetime_objects = []
for dt_str in datetimes:
    try:
        dt_obj = datetime.strptime(dt_str, '%m/%d/%Y %I:%M %p')
        datetime_objects.append(dt_obj)
    except ValueError as e:
        print(f"Error converting '{dt_str}' to datetime object:", e)

# Print the converted datetime objects
print("Converted datetime objects:")
print(datetime_objects)

# Write the datetime objects to a CSV file
csv_file_path = 'datetime_info.csv'
with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Datetime'])
    for dt_obj in datetime_objects:
        writer.writerow([dt_obj.strftime('%Y-%m-%d %H:%M:%S')])

print(f"CSV file '{csv_file_path}' has been created.")

'''