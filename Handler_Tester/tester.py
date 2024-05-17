# class tester for Master PC
# date:5/6/2024
import time
import serial

class Tester:
    def __init__(self, port):
        self.port = port
        self.serial = serial.Serial(port, baudrate=115200, timeout=2)
        time.sleep(2)  # Wait for the serial port to initialize

    def send_message(self, message):
        message += "\r\n"  # Append CR LF
        timestamp = time.strftime("%Y-%m-%d, %H:%M:%S")
        print(f"{timestamp}, [T->H] {message}")
        self.serial.write(message.encode())

    def receive_message(self):
        received_message = self.serial.readline().decode().strip()
        # print(f"Tester Received: {received_message}")
        return received_message

    def close(self):
        self.serial.close()
