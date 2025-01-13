import sys
import os
import re


# Get command-line arguments
if len(sys.argv) != 5:
    print("Usage: script.py <SN> <Host> <Temp> <DNA>")
    sys.exit(1)

sn = sys.argv[1]
dna = sys.argv[2]
host = sys.argv[3]
temp = sys.argv[4]

# Construct the log file path
log_file = "../Data/logs/mipi_dphy_lpbk_4_5G_{}_{}_{}_{}.log".format(sn, dna, host, temp)
#log_file = f"../../Data/logs/mipi_dphy_lpbk_4_5G_{sn}_{dna}_{host}_{temp}.log"

# Print the log file path
#print(f"Log file path: {log_file}")
print("Log file path: {}".format(log_file))


# Check if log file exists
if os.path.isfile(log_file):
    with open(log_file, 'r') as file:
        # Search for the pattern '900D900D' in the log file
        found_lines = [line for line in file if '900D900D' in line]
        
    if found_lines:
        print("Matching lines:")
        for line in found_lines:
            print(line.strip())
    else:
        print("No matching lines found.")
    
    #print(f"Finished processing log file for SN: {sn}, Host: {host}, Temp: {temp}, DNA: {dna}")
    print("Finished processing log file for SN: {}, Host: {}, Temp: {}, DNA: {}".format(sn, host, temp, dna))

else:
    #print(f"Error: Log file does not exist: {log_file}")
    print("Error: Log file does not exist: {}".format(log_file))
    sys.exit(1)
