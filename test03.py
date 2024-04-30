import subprocess
import re
import csv
from datetime import datetime
import pandas as pd

# Run the 'dir /OD' command and capture its output
output = subprocess.check_output(['cmd', '/C', 'dir', '/OD']).decode('utf-8')

# Print the output for debugging
print("Output:", output)

# Regular expression pattern to extract date-time and filename
#pattern = r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[AP]M)\s+\d+\s+(sn(X\w{16}))_m40_result\.txt"
pattern = r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[AP]M)\s+\d+\s+sn(X\w{15})_m40_result\.txt"

# Find all matches in the directory listing
matches = re.findall(pattern, output)

# Print the matches
for match in matches:
    print("Date-Time:", match[0])
    print("Filename:", match[1])
    print()

# Create a DataFrame
df = pd.DataFrame(matches, columns=["Date-Time", "Serial No."])

# Save to Excel
df.to_excel("output.xlsx", index=False)