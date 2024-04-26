import os
'''
Below is an example of a Python script that appends log files into one file
'''

def append_logs(log_directory, output_file):
    try:
        # Change to the log directory
        os.chdir(log_directory)

        # Get a list of all log files in the directory
        log_files = [file for file in os.listdir() if file.endswith('.log')]

        # Open the output file in append mode
        with open(output_file, 'a') as output:
            # Iterate through each log file and append its content to the output file
            for log_file in log_files:
                with open(log_file, 'r') as log:
                    output.write(log.read())

        print(f"Log files appended successfully to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

# Specify the path to the directory containing log files
log_directory = "/path/to/logs"

# Specify the output file
output_file = "/path/to/output.log"

# Call the function to append logs
append_logs(log_directory, output_file)
