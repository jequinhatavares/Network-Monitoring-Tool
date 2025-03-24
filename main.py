import socket
import networkx as nx
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading

# Create the Dash app
app = dash.Dash(__name__)

# UDP Configuration
UDP_IP = "192.168.1.85"
UDP_PORT = 5000
G = nx.DiGraph()  # Directed graph to store network nodes


# Function to generate Plotly figure from NetworkX
def get_graph_figure():
    pos = nx.spring_layout(G)  # Layout for positioning nodes
    edge_x, edge_y = [], []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='gray')))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=10, color="lightblue"),
        text=node_text, textposition="top center"
    ))

    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# Dash layout
app.layout = html.Div([
    html.H1("Real-Time Network Visualization"),
    dcc.Graph(id="network-graph"),
    dcc.Interval(id="interval", interval=1000, n_intervals=0)  # Updates every second
])

# Dash callback to update graph
@app.callback(Output("network-graph", "figure"), [Input("interval", "n_intervals")])
def update_graph(n):
    return get_graph_figure()

# Function to listen for UDP packets and update graph
def udp_listener(sock):
    print(f"Listening for UDP packets on port {UDP_PORT}...")
    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode().strip()

        try:
            node_id, parent_id, rssi = message.split()

            G.add_node(node_id)
            if parent_id != "None":
                G.add_edge(parent_id, node_id, weight=float(rssi))

            print(f"Received: Node {node_id}, Parent {parent_id}, RSSI {rssi}")

        except ValueError:
            print(f"Invalid message received: {message}")

def start_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket reuse
    sock.bind((UDP_IP, UDP_PORT))  # Bind the socket
    threading.Thread(target=udp_listener, args=(sock,), daemon=True).start()


# Run UDP listener in a separate thread to avoid blocking Dash
start_listener()

# Run Dash app
if __name__ == "__main__":
    app.run(debug=True)
