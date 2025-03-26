import socket
import time

# Server (root node) IP and port
UDP_IP = "192.168.1.85"
UDP_PORT = 5000

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Example nodes and their parent relationships
nodes = ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5"]
parents = {
    "1.1.1.1": "None",
    "2.2.2.2": "1.1.1.1",
    "3.3.3.3": "1.1.1.1",
    "4.4.4.4": "2.2.2.2",
    "5.5.5.5": "3.3.3.3"
}
nodes2 = ["1", "2", "3", "4", "5"]
parents2 = {
    "1": "None",
    "2": "1",
    "3": "1",
    "4": "2",
    "5": "3"
}


while True:
    for node2, parent2 in parents.items():
        message = f"10 {node2} {parent2}"
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {message}")
        time.sleep(2)   #Send updates every 20 seconds

    time.sleep(2)