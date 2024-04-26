import socket

def send_tcp_packet(target_ip, target_port, message):
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Connect to the target
            s.connect((target_ip, target_port))
            # Send the message
            s.sendall(message.encode())
            print("TCP packet sent successfully")
            # Receive response
            response = s.recv(1024)  # Adjust buffer size as needed
            print("Received response:", response.decode())
        except Exception as e:
            print(f"Failed to send TCP packet: {e}")

# Usage example
target_ip = '192.168.137.1'  # Replace with the target IP address
target_port = 1001       # Replace with the target port
message = "Hello, TCP! Sending Msg to Master PC"   # Message to send
send_tcp_packet(target_ip, target_port, message)
