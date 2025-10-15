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

COM = 'COM3'
arduino = serial.Serial(port=COM, baudrate=115200, timeout=.1)

GRAPH_FILE = "graph.json"



def save_graph(g):
    g_json = json_graph.node_link_data(g, edges="links")
    json.dump(g_json, open(GRAPH_FILE, 'w'), indent=2)

# Initialize with an empty graph when the program starts
def initialize_graph():
    if os.path.exists(GRAPH_FILE):
        os.remove(GRAPH_FILE)  # Remove existing graph file
    G = nx.DiGraph()
    save_graph(G)

# Call initialization function before creating the Dash app
initialize_graph()

# Create the Dash app
app = dash.Dash(__name__)



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

MESSAGE_TYPE_NAMES = {
    0: "PARENT_DISCOVERY_REQUEST",
    1: "PARENT_INFO_RESPONSE",
    2: "CHILD_REGISTRATION_REQUEST",
    3: "FULL_ROUTING_TABLE_UPDATE",
    4: "PARTIAL_ROUTING_TABLE_UPDATE",
    5: "TOPOLOGY_BREAK_ALERT",
    6: "TOPOLOGY_RESTORED_NOTICE",
    7: "PARENT_RESET_NOTIFICATION",
    8: "MONITORING_MESSAGE",
    9: "DATA_MESSAGE",
    10: "MIDDLEWARE_MESSAGE"
}

# Mapping of neural network message subtypes
NEURAL_NETWORK_MESSAGE_NAMES = {
    0: "NN_ASSIGN_COMPUTATION",
    1: "NN_ASSIGN_INPUT",
    2: "NN_ASSIGN_OUTPUT",
    3: "NN_ASSIGN_OUTPUT_TARGETS",
    4: "NN_NEURON_OUTPUT",
    5: "NN_FORWARD",
    6: "NN_NACK",
    7: "NN_ACK",
    8: "NN_WORKER_REGISTRATION",
    9: "NN_INPUT_REGISTRATION",
    10: "NN_OUTPUT_REGISTRATION",
}

# Middleware strategy types
MIDDLEWARE_STRATEGY_NAMES = {
    0: "INJECT",
    1: "PUBSUB",
    2: "TOPOLOGY",
    3: "NONE"
}

# Middleware message subtypes
INJECT_MESSAGE_NAMES = {
    0: "INJECT_NODE_METRIC_UPDATE",
    1: "INJECT_NETWORK_METRICS_UPDATE"
}

PUBSUB_MESSAGE_NAMES = {
    0: "PUBSUB_SUBSCRIBE",
    1: "PUBSUB_UNSUBSCRIBE",
    2: "PUBSUB_ADVERTISE",
    3: "PUBSUB_UNADVERTISE",
    4: "PUBSUB_NODE_TOPICS_UPDATE",
    5: "PUBSUB_NETWORK_TOPICS_UPDATE"
}

TOPOLOGY_MESSAGE_NAMES = {
    0: "TOP_PARENT_LIST_ADVERTISEMENT_REQUEST",
    1: "TOP_PARENT_LIST_ADVERTISEMENT",
    2: "TOP_PARENT_ASSIGNMENT_COMMAND",
    3: "TOP_METRICS_REPORT",
    4: "TOP_NODE_UPDATE"
}

join_metrics = []
parent_recovery_metrics = []
message_metrics = []
message_continuous_metrics = []
end_to_end_delay_metrics = []
app_init_metrics = []
app_inference_metrics = []

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
                            # Remove the node only if it exists
                            if node_IP in G:
                                G.remove_node(node_IP)

                            G.add_node(node_IP)
                            if parent_IP != "0.0.0.0":
                                G.add_edge(parent_IP, node_IP)
                            save_graph(G)
                            pass

                        case ['8', '1', node_IP]:  # Deleted node message
                            G = load_graph()
                            if node_IP in G:
                                G.remove_node(node_IP)
                            save_graph(G)
                            pass

                        case ['8', '3', device_type, init_time, search_time, join_time]:  # Reporting State machine times
                            print(f"Metrics: {device_type=} {init_time=} {search_time=} {join_time=}")
                            join_metrics.append(dict(
                                type='ESP8266' if device_type == '1' else 'ESP32' if device_type == '2' else 'RPI',
                                init_time=init_time,
                                search_time=search_time,
                                join_time=join_time,
                            ))
                            #print(f"{data=}")

                        case ['8', '4', device_type, parent_recovery_time]:  # Reporting Parent Recovery time
                            print(f"Metrics: {device_type=} {parent_recovery_time=}")
                            parent_recovery_metrics.append(dict(
                                type='ESP8266' if device_type == '1' else 'ESP32' if device_type == '2' else 'RPI',
                                parent_recovery_time=parent_recovery_time,
                            ))
                            #print(f"{data=}")


                        case ['8', '5',device_type,node_ip,monitoring_time,n_routing,bytes_routing,n_lifecycle,bytes_lifecycle,n_middleware,bytes_middleware,
                              n_app,bytes_app,n_monitoring,bytes_monitoring]:  # Reporting the messages received from each layer

                            message_metrics.append(dict(
                                type='ESP8266' if device_type == '1' else 'ESP32' if device_type == '2' else 'RPI',
                                node_ip=node_ip,


                                monitoring_time=monitoring_time,
                                routing_msg_count=n_routing,
                                routing_bytes_count=bytes_routing,
                                lifecycle_msg_count=n_lifecycle,
                                lifecycle_bytes_count=bytes_lifecycle,
                                middleware_msg_count=n_middleware,
                                middleware_bytes_count=bytes_middleware,
                                app_msg_count=n_app,
                                app_bytes_count=bytes_app,
                                monitoring_msg_count=n_monitoring,
                                monitoring_bytes_count=bytes_monitoring,
                            ))
                            #print(f"{data=}")


                        case ['8', '6', message_type_code, *rest]: #Message Continuous
                            # MONITORING_MESSAGE MESSAGE_CONTINUOUS[Message Type] [Strategy Type] [Message SubType] [N Bytes] or
                            # MONITORING_MESSAGE MESSAGE_CONTINUOUS [Message Type] [Message SubType] [N Bytes]

                            # Convert message type to integer
                            msg_type_int = int(message_type_code)
                            msg_type_name = MESSAGE_TYPE_NAMES.get(msg_type_int, None)

                            # Handle different message types
                            if msg_type_name == "MIDDLEWARE_MESSAGE":
                                # MIDDLEWARE_MESSAGE format: [strategy_type] [message_subtype] [n_bytes]
                                if len(rest) >= 3:
                                    strategy_type, message_subtype, n_bytes = rest[0], rest[1], rest[2]
                                    strategy_int = int(strategy_type)
                                    msg_subtype_int = int(message_subtype)

                                    # Get strategy name
                                    strategy_name = MIDDLEWARE_STRATEGY_NAMES.get(strategy_int,None)

                                    # Get subtype name based on strategy
                                    if strategy_int == 0:  # INJECT
                                        subtype_name = INJECT_MESSAGE_NAMES.get(msg_subtype_int,None)
                                    elif strategy_int == 1:  # PUBSUB
                                        subtype_name = PUBSUB_MESSAGE_NAMES.get(msg_subtype_int,None)
                                    elif strategy_int == 2:  # TOPOLOGY
                                        subtype_name = TOPOLOGY_MESSAGE_NAMES.get(msg_subtype_int,None)

                                    else:
                                        subtype_name = None

                                    # Append to the metrics list
                                    message_continuous_metrics.append(dict(
                                        timestamp=time.time(),
                                        messageType=msg_type_name,
                                        strategyType=strategy_name,
                                        messageSubtype=subtype_name,
                                        n_bytes=int(n_bytes)
                                    ))
                                else:
                                    print(f"Error: Invalid MIDDLEWARE_MESSAGE format: {data}")

                            else:
                                # Other message types format: [message_subtype] [n_bytes]
                                if len(rest) >= 2:
                                    message_subtype, n_bytes = rest[0], rest[1]
                                    msg_subtype_int = int(message_subtype)

                                    # Determine subtype name only for DATA_MESSAGE
                                    if msg_type_name == "DATA_MESSAGE":
                                        msg_subtype_name = NEURAL_NETWORK_MESSAGE_NAMES.get(msg_subtype_int,None)
                                    else:# subType=-1
                                        msg_subtype_name = None  # other messages don't have subtypes


                                    # Append to the metrics list
                                    message_continuous_metrics.append(dict(
                                        timestamp=time.time(),
                                        messageType=msg_type_name,
                                        strategyType=None,
                                        messageSubtype=msg_subtype_name,
                                        n_bytes=int(n_bytes)
                                    ))
                                else:
                                    print(f"Error: Invalid message format for {msg_type_name}: {data}")

                            #print(f"{data=}")


                        case ['8', '7', *delay_data]:  # END_TO_END_DELAY message with variable node entries
                            # Parse format: [node_ip] [delay] [hops] [node_ip] [delay] [hops] ...

                            # Process data in chunks of 3 (ip, delay, hops)
                            for i in range(0, len(delay_data), 3):
                                if i + 2 < len(delay_data):  # Ensure we have a complete triplet
                                    node_ip = delay_data[i]
                                    delay_value = int(delay_data[i + 1])
                                    hop_count = int(delay_data[i + 2])

                                    end_to_end_delay_metrics.append(dict(
                                        node_ip=node_ip,
                                        latency=delay_value,
                                        hop_count=hop_count
                                    ))

                            print(f"Parsed end-to-end delay metrics: {end_to_end_delay_metrics}")

                        case ['8', '8', *app_data]:  # Reporting Data Level Information
                            if len(app_data) > 0:
                                message_type = int(app_data[0])

                                if message_type == 0:  # NEURAL_NETWORK_SETUP_TIME
                                    #NEURAL_NETWORK_SETUP_TIME [NN SetupTime] [Missing ACKs]
                                    if len(app_data) >= 2:
                                        app_init_metrics.append(dict(
                                            setup_time_ms=int(app_data[1]),
                                            missing_acks=int(app_data[2])
                                        ))
                                    else:
                                        print("Warning: Incomplete setup time data")

                                elif message_type == 1:  # NEURAL_NETWORK_INFERENCE_TIME
                                    #NEURAL_NETWORK_INFERENCE_TIME [StrategyType] [Inference Id] [Inference Time] [NACK Count] [N outputs] [Output Value 1]...[OutputValueN]
                                    if len(app_data) >= 6:
                                        n_outputs = int(app_data[5])
                                        if len(app_data) >= 6 + n_outputs:
                                            strategy_name = MIDDLEWARE_STRATEGY_NAMES.get(int(app_data[1]), None)


                                            app_inference_metrics.append(dict(
                                                strategy_type=strategy_name,
                                                inference_id=int(app_data[2]),
                                                inference_time_ms=int(app_data[3]),
                                                nack_count=int(app_data[4]),
                                                n_outputs=n_outputs,
                                                output_values=[float(app_data[6 + i]) for i in range(n_outputs)]
                                            ))
                                        else:
                                            print(f"Warning: Insufficient data for {n_outputs} outputs")
                                    else:
                                        print("Warning: Incomplete inference time data")
                                else:
                                    print(f"Warning: Unknown app message type {message_type}")
                            else:
                                print("Warning: Empty app data received")


                # if viz_message_type == "0": #New node message
                #   logging_module,message_type, viz_message_type, node_IP, parent_IP = message.split()
                #   print("DEBUG MESSAGE")
                except ValueError:
                    pass

            except ValueError:
                pass


def cli():

    n_join: int = len([file for file in os.listdir('logs') if file.startswith('run-join-')])
    n_parent_recovery: int = len([file for file in os.listdir('logs') if file.startswith('run-parent-recovery-')])
    n_messages: int = len([file for file in os.listdir('logs') if file.startswith('run-messages-')])
    n_continuous_messages: int = len([file for file in os.listdir('logs') if file.startswith('run-continuous-messages-')])
    n_end_to_end_delay: int = len([file for file in os.listdir('logs') if file.startswith('run-end-to-end-delay-')])
    n_app_init: int = len([file for file in os.listdir('logs') if file.startswith('run-app-init-')])
    n_app_inference: int = len([file for file in os.listdir('logs') if file.startswith('run-app-inference-')])

    while True:
        cmd = input(
            "Press [1] to print metrics\n"
            "Press [2] to generate JSON\n"
            "Press [8] to request root to measure end-to-end delay\n")

        print(f"Command: {cmd}")
        match cmd:
            case '1':
                print(f"{join_metrics=} \n{parent_recovery_metrics=} \n{message_metrics=} \n{message_continuous_metrics=} "
                      f"\n{end_to_end_delay_metrics=} \n{app_init_metrics=} \n{app_inference_metrics=} ")
            case '2':
                with open(f'logs/run-join-{n_join}.json', 'w', encoding='utf-8') as f:
                    json.dump(join_metrics, f)
                with open(f'logs/run-parent-recovery-{n_parent_recovery}.json', 'w', encoding='utf-8') as f:
                    json.dump(parent_recovery_metrics, f)
                with open(f'logs/run-messages-{n_messages}.json', 'w', encoding='utf-8') as f:
                    json.dump(message_metrics, f)
                with open(f'logs/run-continuous-messages-{n_continuous_messages}.json', 'w', encoding='utf-8') as f:
                    json.dump(message_continuous_metrics, f)
                with open(f'logs/run-end-to-end-delay-{n_end_to_end_delay}.json', 'w', encoding='utf-8') as f:
                    json.dump(end_to_end_delay_metrics, f)
                with open(f'logs/run-app-init-{n_app_init}.json', 'w', encoding='utf-8') as f:
                    json.dump(app_init_metrics, f)
                with open(f'logs/run-app-inference-{n_app_inference}.json', 'w', encoding='utf-8') as f:
                    json.dump(app_inference_metrics, f)

            case '8':
                arduino.write(b'\r\n')
                time.sleep(0.5)
                arduino.write(b'8')
                time.sleep(3)
                arduino.write(b'7')

threading.Thread(target=read_serial, args=(), daemon=True).start()
threading.Thread(target=cli, args=(), daemon=True).start()

# while True:
# num = input("Enter a number: ") # Taking input from user
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    # while True:
    #   continue
