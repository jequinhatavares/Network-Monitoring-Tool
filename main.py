import socket
import json
import networkx as nx
from networkx.readwrite import json_graph
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading

GRAPH_FILE = "graph.json"

# Create the Dash app
app = dash.Dash(__name__)

# UDP Configuration
my_IP = "192.168.1.85"
UDP_PORT = 5000
#G = nx.DiGraph()  # Directed graph to store network nodes

def save_graph(g):
    g_json = json_graph.node_link_data(g)
    json.dump(g_json,open(GRAPH_FILE,'w'),indent=2)

def load_graph():
    with open(GRAPH_FILE) as f:
        js_graph = json.load(f)
    return json_graph.node_link_graph(js_graph)


def get_graph_figure(G):
    pos = nx.spring_layout(G, seed=42)  # Node positions

    # Edge coordinates
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Node coordinates and labels
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

    # Create figure
    fig = go.Figure()

    # Add edges as gray lines
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='lightgray'),
        hoverinfo='none'
    ))

    # Add nodes as blue markers with dark border
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=40, color="pink", line=dict(width=2, color="black")),
        text=node_text,
        textposition="top center",
        hoverinfo="text"
    ))

    # Layout tweaks for a cleaner look
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white"
    )

    return fig

app.layout = html.Div([
    html.H1("Real-Time Network Visualization"),
    dcc.Graph(id="network-graph"),
    dcc.Interval(id="graph-update", interval=1000, n_intervals=0)
])

@app.callback(Output("network-graph", "figure"), [Input("graph-update", "n_intervals")])
def update_graph(n):
    G = load_graph()
    return get_graph_figure(G)

def udp_listener(sock):
    print(f"Listening for UDP packets on port {UDP_PORT}...")
    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode().strip()
        try:
            message_type, *_ = message.split()
            if message_type == "10":
                message_type, node_IP, parent_IP = message.split()

                G = load_graph()
                G.add_node(node_IP)
                if parent_IP != "None":
                    G.add_edge(parent_IP, node_IP)
                save_graph(G)
                #print("Nodes in G on UDP:", G.nodes())
                #print("Edges in G on UDP:", G.edges())
        except ValueError:
            print(f"Invalid message received: {message}")

def start_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_IP, UDP_PORT))
    threading.Thread(target=udp_listener, args=(sock,), daemon=True).start()

save_graph(nx.DiGraph())
start_listener()

if __name__ == "__main__":
    app.run(debug=True)
