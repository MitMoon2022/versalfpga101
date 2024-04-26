import shutil

# Source file path
source_file0 = "/path/to/source/file"   #original
source_file1 = r"C:\Users\jeffiot\OneDrive - Advanced Micro Devices Inc\Documents\XA VST S50 proj\run_summary.log"

source_file2 = r"\\SONATA.xilinx.com\xap_charserv2\engineering\Characterization\charmnt\Robot-SLT\XAP\SLT-01\Project\Versal\VC1702_VE1752\XAVST\XAVST_TP_REPO_comb1\ALL_LPnom_R001\Data\logs\run_summary.log"

# Destination directory (local directory)
destination_directory0 = "local_directory/"  #original
destination_directory1 = r"C:\Users\jeffiot\OneDrive - Advanced Micro Devices Inc\Documents\XA VST S50 proj\cmpLog"

try:
    shutil.copy(source_file2, destination_directory1)
    print(f"File '{source_file2}' copied to '{destination_directory1}' successfully.")
except FileNotFoundError:
    print(f"Source file '{source_file2}' not found.")
except PermissionError:
    print("Permission denied. Make sure you have the necessary permissions.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
