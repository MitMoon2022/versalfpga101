import subprocess

def list_files_ordered_by_date():
    try:
        # Execute the 'dir /OD' command within the command prompt
        output = subprocess.check_output(['cmd', '/C', 'dir', '/OD']).decode('utf-8')
        print(output)
    except Exception as e:
        print("Error:", e)

# Call the function to list files ordered by date
list_files_ordered_by_date()