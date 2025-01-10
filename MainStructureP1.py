import sys
import os


def construct_log_file_path(sn, dna, host,temp):
    """Construct the log file path based on input parameters."""
    return f"../Data/logs/mipi_dphy_lpbk_4_5G_{sn}_{dna}_{host}_{temp}.log"


def check_log_file_exists(log_file):
    """Check if the log file exists."""
    if not os.path.isfile(log_file):
        print(f"Error: Log file does not exist: {log_file}")
        sys.exit(1)


def process_log_file(log_file):
    """Search for a specific pattern in the log file and print matching lines."""
    with open(log_file, 'r') as file:
        found_lines = [line.strip() for line in file if '900D900D' in line]
    
    if found_lines:
        print("Matching lines:")
        for line in found_lines:
            print(line)
    else:
        print("No matching lines found.")


def main():
    """Main entry point of the script."""
    if len(sys.argv) != 5:
        print("Usage: script.py <SN> <DNA> <Host> <Temp>")
        sys.exit(1)

    sn, host, temp, dna = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    # Construct and print the log file path
    log_file = construct_log_file_path(sn, host, temp, dna)
    print(f"Log file path: {log_file}")

    # Check if the log file exists
    check_log_file_exists(log_file)

    # Process the log file
    process_log_file(log_file)

    # Print completion message
    print(f"Finished processing log file for SN: {sn}, Host: {host}, Temp: {temp}, DNA: {dna}")


if __name__ == "__main__":
    main()
