import socket
import networkx as nx
import matplotlib.pyplot as plt
import time

# UDP Configuration
my_IP = "192.168.1.85"  # Your machine's IP
UDP_PORT = 5000
G = nx.DiGraph()  # Directed graph

# Matplotlib setup
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots(figsize=(8, 6))

# Add an initial root node to avoid an empty graph
G.add_node("1.1.1.1")

def listen_for_udp(sock):
    """Listen for UDP messages and update the graph."""
    try:
        data, _ = sock.recvfrom(1024)
        message = data.decode().strip()
        print(f"Received UDP message: {message}")  # Debugging output

        parts = message.split()
        if len(parts) != 3 or parts[0] != "10":
            print("Invalid message format, ignoring.")
            return  # Ignore malformed messages

        _, node_IP, parent_IP = parts
        if node_IP not in G:
            G.add_node(node_IP)
        if parent_IP != "None":
            G.add_edge(parent_IP, node_IP)

        print(f"Graph updated: Nodes={list(G.nodes)}, Edges={list(G.edges)}")  # Debug

    except BlockingIOError:
        pass  # No data available, continue execution

def plot_graph():
    """Update the graph visualization dynamically."""
    ax.clear()  # Clear the previous graph
    pos = nx.spring_layout(G, seed=42)  # Positioning nodes

    # Draw nodes and edges
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=2000, node_color="lightblue",
            font_size=12, font_weight="bold", edge_color="gray")

    ax.set_title("Real-Time Network Visualization")
    fig.canvas.draw()  # Force update
    fig.canvas.flush_events()  # Handle GUI updates

if __name__ == "__main__":
    # Setup the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_IP, UDP_PORT))
    sock.setblocking(False)  # Non-blocking mode

    print(f"Listening for UDP packets on port {UDP_PORT}...")

    try:
        while True:
            listen_for_udp(sock)  # Process UDP messages
            plot_graph()  # Update visualization
            time.sleep(1)  # Prevent excessive CPU usage
    except KeyboardInterrupt:
        print("Stopped by user.")
