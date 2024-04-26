import serial
import time

# Get user input for serial ports
#tx_port = input("Enter COM port for sending messages (e.g. COM1): ")
rx_port = input("Enter COM port for receiving messages (e.g. COM2): ")

# Open serial ports for communication
#ser_tx = serial.Serial(tx_port, 9600, timeout=100)
ser_rx = serial.Serial(rx_port, 9600, timeout=100)
'''
def send_message(ser, message):
    ser.write(message.encode())
    print(f"Sent: {message}")
'''
def receive_message(ser):
    received_message = ser.readline().decode().strip()
    print(f"Received: {received_message}")
    return received_message
#//=============================================================================
# Send 10 messages from tx_port
''' 
for i in range(1, 11):
    message = f"Message {i}\n"
    send_message(ser_tx, message)
    time.sleep(1)
'''
# Receive messages from rx_port
expected_sequence = 1
start_time = time.time()
while True:
    received_message = receive_message(ser_rx)
    if received_message == f"Message {expected_sequence}":
        expected_sequence += 1
    if expected_sequence == 11:
        print("All messages received successfully.")
        break
    elif time.time() - start_time > 20:  # Timeout after 20 seconds
        print("Timeout: Not all messages received")
        break

# Close serial ports
ser_rx.close()