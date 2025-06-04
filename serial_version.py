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
    json.dump(g_json,open(GRAPH_FILE,'w'),indent=2)

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


def read_serial():

   #arduino.write(bytes(x, 'utf-8'))
   print(f"Listening for serial on {COM}...")
   while True:
      #time.sleep(0.05)
      data = arduino.readline()
      if data != b'':
         try:
            message = data.decode().strip()

            print(f"{message}")
            try:
               logging_module, message_type, *msg_payload = message.split()

               if logging_module == '[D]':

                  #viz_message_type, *_ = msg_payload.split()

                  match msg_payload:

                     case ['0', node_IP]: #New node message
                        G = load_graph()
                        G.add_node(node_IP)
                        if parent_IP != "-1.-1.-1.-1":
                          G.add_edge(parent_IP, node_IP)
                        save_graph(G)
                        pass

                     case['1', node_IP, parent_IP]:  # Deleted node message
                        G = load_graph()
                        G.delete_node(node_IP)
                        if parent_IP != "-1.-1.-1.-1":
                            G.add_edge(parent_IP, node_IP)
                        save_graph(G)
                        pass

                  #if viz_message_type == "0": #New node message
                  #   logging_module,message_type, viz_message_type, node_IP, parent_IP = message.split()
                  #   print("DEBUG MESSAGE")

            except ValueError:
               print(f"Invalid message received: {message}")
               print(f"Logging Module: {logging_module}")

         except ValueError:
            pass



threading.Thread(target=read_serial, args=(), daemon=True).start()


#while True:
   #num = input("Enter a number: ") # Taking input from user
if __name__ == "__main__":
   app.run(debug=True, use_reloader=False)
    #while True:
    #   continue