import os
import time
from unittest import skipIf
import serial
import json
import networkx as nx
from networkx.readwrite import json_graph
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading

COM = 'COM4'
arduino = serial.Serial(port=COM, baudrate=115200, timeout=.1)

GRAPH_FILE = "graph.json"

# Create the Dash app
app = dash.Dash(__name__)


def save_graph(g):
    g_json = json_graph.node_link_data(g, edges="links")
    json.dump(g_json, open(GRAPH_FILE, 'w'), indent=2)


def load_graph():
    with open(GRAPH_FILE) as f:
        js_graph = json.load(f)
    return json_graph.node_link_graph(js_graph, edges="links")


def get_graph_figure(G):
    pos = nx.spring_layout(G, seed=42)  # Node positions

    # Identify root nodes (nodes with no incoming edges)
    root_nodes = [node for node in G.nodes if G.in_degree(node) == 0]

    # Edge coordinates
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Node coordinates and labels
    node_x, node_y, node_text, node_colors = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

        # Assign different colors for root nodes
        if node in root_nodes:
            node_colors.append("pink")  # Root nodes in red
        else:
            node_colors.append("blue")  # Other nodes in pink

    # Create figure
    fig = go.Figure()

    # Add edges as gray lines
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='lightgray'),
        hoverinfo='none'
    ))

    # Add nodes with custom colors
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=40, color=node_colors, line=dict(width=2, color="black")),
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

metrics = []
def read_serial():
    # arduino.write(bytes(x, 'utf-8'))
    print(f"Listening for serial on {COM}...")
    time.sleep(2)
    arduino.write(b'\r\n')
    while True:
        # time.sleep(0.05)
        data = arduino.readline()

        if data != b'':
            try:
                message = data.decode().strip()

                print(f"{message}")
                try:
                    #message_type, *msg_payload =

                # viz_message_type, *_ = msg_payload.split()

                    match message.split():

                        case ['8', '0', node_IP, parent_IP]:  # New node message
                            G = load_graph()
                            G.add_node(node_IP)
                            if parent_IP != "0.0.0.0":
                                G.add_edge(parent_IP, node_IP)
                            save_graph(G)
                            pass

                        case ['8', '1', node_IP]:  # Deleted node message
                            G = load_graph()
                            G.delete_node(node_IP)
                            if parent_IP != "0.0.0.0":
                                G.add_edge(parent_IP, node_IP)
                            save_graph(G)
                            pass

                        case ['8', '3', device_type, init_time, search_time, join_time]:  # Reporting State machine times
                            print(f"Metrics: {device_type=} {init_time=} {search_time=} {join_time=}")
                            metrics.append(dict(
                                type='ESP8266' if device_type == '1' else 'ESP32' if device_type == '2' else 'RPI',
                                init_time=init_time,
                                search_time=search_time,
                                join_time=join_time,
                            ))
                            print(f"{data=}")

                # if viz_message_type == "0": #New node message
                #   logging_module,message_type, viz_message_type, node_IP, parent_IP = message.split()
                #   print("DEBUG MESSAGE")
                except ValueError:
                    pass

            except ValueError:
                pass


def cli():
    n_join: int = len([file for file in os.listdir('logs') if file.startswith('run-join-')])
    while True:
        cmd = input(
            "Press [1] to print metrics\n"
            "Press [2] to generate JSON\n")
        print(f"Command: {cmd}")
        match cmd:
            case '1':
                print(f"{metrics=}")
            case '2':
                with open(f'logs/run-join-{n_join}.json', 'w', encoding='utf-8') as f:
                    json.dump(metrics, f)

threading.Thread(target=read_serial, args=(), daemon=True).start()
threading.Thread(target=cli, args=(), daemon=True).start()

# while True:
# num = input("Enter a number: ") # Taking input from user
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    # while True:
    #   continue
