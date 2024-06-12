# from tester import Tester
from tester_abort import Tester
# from handler import Handler
from handler_abort import Handler
import serial
import time
import re
import random
import string
import sys

def generate_random_string(length):
    alphabet = string.ascii_uppercase + string.digits
    return 'X' + ''.join(random.choice(alphabet) for _ in range(length-1))

def generate_binary_list(length):
    return [random.choice([0, 1]) for _ in range(length)]

# Input COM ports for tester and handler
timestamp = time.strftime("%Y-%m-%d, %H:%M:%S")
tester_port = input("Enter COM port for tester: ")
handler_port = input("Enter COM port for handler: ")

# Create instances of tester and handler
tester = Tester(tester_port)
handler = Handler(handler_port)
print(f"{timestamp} INITIALIZE	Initializing system ...")
print(f"{timestamp} INITIALIZE	COM Port {tester_port} and {handler_port} connected")

# Prompt user to input timeout_seconds and no_of_units
timeout_seconds = int(input("Enter timeout in seconds: "))
no_of_units = int(input("Enter number of units: "))
# test_result = generate_binary_list(no_of_units)

# Randomly generate barcodes
barcode_list = []
for i in range(no_of_units):
    barcode = generate_random_string(16)
    barcode_list.append(barcode)
print(f"{no_of_units} barcodes are randomly generated for simulation: {barcode_list}")
time.sleep(2)

# Handshake command
tester_command = ["FR?", "SVID:35915", "SVID:35916", "ECID:37228,PA,PB"]
handler_command = ["FR0", "SVID:1", "SVID:1", "ECHOOK"]

t = 0
h = 0
tester.send_message(tester_command[t])
time.sleep(1)
while True:
    if tester.receive_message() == handler_command[t]:
        if handler_command[t] == "ECHOOK":
            # print("WAITFORECHOCODEOK	Received--ECHOCODEOK[CR][CR][LF]")
            break
        t += 1
        tester.send_message(tester_command[t])
        time.sleep(1)
    if handler.receive_message() == tester_command[h]:
        handler.send_message(handler_command[h])
        h += 1
        time.sleep(1)

time.sleep(2) 
# Start Testing
# Tester Waiting for SOT
# Handler place DUT to Socket
# Check contact
# Ready to send SOT
pass

# SOT
start_time = time.time()
for i in range(no_of_units):
    site = input("Enter site number:")
    test_result = str(input("Enter test result (0 or 1):"))
    barcode_msg = "BARCODE:" + ''.join('0,' for _ in range(32-int(site))) + barcode_list[i] + ''.join(',0' for _ in range(int(site)))
    barcode_msg = barcode_msg[:-2]
    while True:
        handler.send_message(f"<<{site}%SOT>>")
        time.sleep(1)
        if tester.receive_message() == f"<<{site}%SOT>>":
            tester.send_message("BARCODE?")
            time.sleep(1)
        if handler.receive_message() == "BARCODE?":
            handler.send_message(barcode_msg)
            time.sleep(1)
        if tester.receive_message() == barcode_msg:
            print("Test flow started... ...")
            # Start running tests...
            time.sleep(2)
            abort = False

            # GUI Trigger Abort
            abort_test = input("Abort test (Y/N):")

            if abort_test == "Y":
                handler.send_message(f"<<{site}%FORCEQUIT>>")
                time.sleep(1)
                if tester.receive_message() == f"<<{site}%FORCEQUIT>>":
                    tester.send_message(f"<<{site}%FORCEQUIT%ACK>>")
                    print(f"Test aborted at site {site}.")
                    break
        
            # Normal flow
            
            elif abort_test == "N":
                while True:
                    time.sleep(2)
                    tester.send_message(f"<<{site}%EOT%{test_result}>>")
                    time.sleep(1)
                    if handler.receive_message() == f"<<{site}%EOT%{test_result}>>":
                        handler.send_message(f"<<{site}%EOT%ACK>>")
                        if test_result == '1':
                            print(f"Test passed at site {site}.")
                        else:
                            print(f"Test failed at site {site}.")
                        break
            break
        
        if time.time() - start_time > timeout_seconds:
            print("Timeout reached. Exiting...")
            break

print("EXIT Application closed")

# Close the serial ports
tester.close()
handler.close()