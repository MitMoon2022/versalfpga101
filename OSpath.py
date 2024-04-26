import os

cwd = os.getcwd()
print("Current working directory:", cwd)

# Specify the subdirectory where you want to extract the files (e.g., "data")
subdirectory = "data"

# Create the full path to the destination directory using os.path.join()
data_directory = os.path.join(cwd, subdirectory)
print("Data directory:", data_directory)

# List the files in the data_directory
files = os.listdir(data_directory)
print("Files in data directory:", files)
