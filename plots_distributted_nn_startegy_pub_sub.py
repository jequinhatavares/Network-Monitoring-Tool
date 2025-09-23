import os

import pandas as pd
import plotly.express as px
import json
import plotly
import plotly.colors as pc


import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_dfs():

    runs = []
    for file in ["logs/distributed_nn_12_strategy_pub_sub/"+f for f in os.listdir("logs/distributed_nn_12_strategy_pub_sub/") if f.startswith('run-app-init')]:
        with open(file,'r') as f:
            runs += json.load(f)
    app_init_df = pd.DataFrame(runs)
    app_init_df = app_init_df.astype({'setup_time_ms': 'int32', 'missing_acks': 'int32'})

    runs = []
    for file in ["logs/distributed_nn_12_strategy_pub_sub/"+f for f in os.listdir("logs/distributed_nn_12_strategy_pub_sub/") if f.startswith('run-app-inference')]:
        with open(file,'r') as f:
            runs += json.load(f)
    app_inference_df = pd.DataFrame(runs)
    app_inference_df = app_inference_df.astype({'strategy_type': 'str','inference_id': 'int32','inference_time_ms': 'int32','nack_count': 'int32'})

    runs = []
    with open('logs/distributed_nn_12_strategy_pub_sub/run-continuous-messages-0.json', 'r') as f:
        runs += json.load(f)
    message_continuous_df = pd.DataFrame(runs)
    message_continuous_df = message_continuous_df.astype(
        {'timestamp': 'float64', 'messageType': 'str', 'strategyType': 'str', 'messageSubtype': 'str',
         'n_bytes': 'int32'})

    return app_init_df,app_inference_df,message_continuous_df


def plot_scatter_message_readable(df: pd.DataFrame):
    # Convert timestamp to relative seconds (starting from 0)
    first_timestamp = df['timestamp'].iloc[0]
    df['relative_time'] = df['timestamp'] - first_timestamp

    # Human-readable main message types
    MESSAGE_TYPE_NAMES = {
        'DATA': 'Data Message',
        'MIDDLEWARE': 'Middleware Message',
        'CONTROL': 'Control Message',  # example if you have other types
        # Add other main types if needed
    }

    # Mapping of neural network message subtypes
    NEURAL_NETWORK_MESSAGE_NAMES = {
        0: "NN Assign Computation",
        1: "NN Assign Input",
        2: "NN Assign Output",
        3: "NN Assign Output Targets",
        4: "NN Neuron Output",
        5: "NN Forward",
        6: "NN NACK",
        7: "NN ACK",
        8: "NN Worker Registration",
        9: "NN Input Registration",
        10: "NN Output Registration",
    }

    # Mapping of PUBSUB (middleware) message subtypes
    PUBSUB_MESSAGE_NAMES = {
        0: "PubSub Subscribe",
        1: "PubSub Unsubscribe",
        2: "PubSub Advertise",
        3: "PubSub Unadvertise",
        4: "PubSub Node Topics Update",
        5: "PubSub Network Topics Update"
    }

    # Map to human-readable names
    def map_message(row):
        if row['messageType'] in ['DATA', 'MIDDLEWARE']:
            if row['strategyType'] == 'NEURAL_NETWORK':
                return NEURAL_NETWORK_MESSAGE_NAMES.get(row['messageSubtype'], f"Unknown ({row['messageSubtype']})")
            elif row['strategyType'] == 'PUBSUB':
                return PUBSUB_MESSAGE_NAMES.get(row['messageSubtype'], f"Unknown ({row['messageSubtype']})")
            else:
                return str(row['messageSubtype'])
        else:
            return MESSAGE_TYPE_NAMES.get(row['messageType'], row['messageType'])

    df['message_readable'] = df.apply(map_message, axis=1)

    # Create scatter plot
    fig = px.scatter(
        df,
        x='relative_time',
        y='n_bytes',
        color='message_readable',
        title='',
        labels={
            'relative_time': 'Time (seconds from start)',
            'n_bytes': 'Message Size (bytes)',
            'message_readable': 'Message Type / Subtype'
        },
        hover_data={
            'relative_time': ':.2f',
            'n_bytes': True,
            'message_readable': True,
            'strategyType': True,
            'messageType': True,
            'messageSubtype': True
        },
        hover_name='message_readable'
    )

    # Layout customization
    fig.update_layout(
        xaxis_title='Time Elapsed (seconds)',
        yaxis_title='Message Size (bytes)',
        legend_title='Message Type / Subtype',
        title={
            'text': 'Network Messages Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica', size=20, color='black')
        },
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.9)'
        ),
        plot_bgcolor='white',
        width=1000,
        height=600
    )

    # Marker customization
    fig.update_traces(
        marker=dict(
            size=14,
            opacity=0.8,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )

    # Axes customization
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )
    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    # Add annotation
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"Total Messages: {len(df)}",
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )

    fig.show()


def plot_scatter_message_continuous2(df: pd.DataFrame):
    # Convert timestamp to relative seconds (starting from 0)
    first_timestamp = df['timestamp'].iloc[0]
    df['relative_time'] = df['timestamp'] - first_timestamp

    # Mapping of data message subtypes (neural network)
    DATA_MESSAGE_SUBTYPES = {
        0: "Assign Computation",
        1: "Assign Input",
        2: "Assign Output",
        3: "Assign Output Targets",
        4: "Neuron Output",
        5: "Forward",
        6: "NACK",
        7: "ACK",
        8: "Worker Registration",
        9: "Input Registration",
        10: "Output Registration",
    }

    # Mapping of middleware message subtypes (pub/sub)
    MIDDLEWARE_MESSAGE_SUBTYPES = {
        0: "Subscribe",
        1: "Unsubscribe",
        2: "Advertise",
        3: "Unadvertise",
        4: "Node Topics Update",
        5: "Network Topics Update"
    }

    # Create human-readable message type labels with subtypes
    def get_full_message_name(row):
        message_type = row['messageType']
        subtype = row.get('messageSubtype', None)

        # Handle DATA_MESSAGE with subtypes
        if message_type == 'DATA_MESSAGE' and pd.notna(subtype):
            if subtype in DATA_MESSAGE_SUBTYPES:
                return DATA_MESSAGE_SUBTYPES[subtype]
            else:
                return f"Data Message - Unknown Subtype {subtype}"

        # Handle MIDDLEWARE_MESSAGE with subtypes
        elif message_type == 'MIDDLEWARE_MESSAGE' and pd.notna(subtype):
            if subtype in MIDDLEWARE_MESSAGE_SUBTYPES:
                return f"Middleware - {MIDDLEWARE_MESSAGE_SUBTYPES[subtype]}"
            else:
                return f"Middleware Message - Unknown Subtype {subtype}"

        # Handle messages without subtypes or unknown types
        else:
            message_type_mapping = {
                'DATA_MESSAGE': 'Data Message',
                'MIDDLEWARE_MESSAGE': 'Middleware Message',
                'PARENT_DISCOVERY_REQUEST': 'Parent Discovery Request',
                'CHILD_REGISTRATION_REQUEST': 'Child Registration Request',
                'MONITORING_MESSAGE': 'Monitoring Message',
                'PARTIAL_ROUTING_TABLE_UPDATE': 'Partial Routing Update',
                'FULL_ROUTING_TABLE_UPDATE': 'Full Routing Update'
            }
            return message_type_mapping.get(message_type, message_type)

    df['messageType_readable'] = df.apply(get_full_message_name, axis=1)

    # Create the scatter plot
    fig = px.scatter(df,
                     x='relative_time',
                     y='n_bytes',
                     color='messageType_readable',
                     title='',
                     labels={
                         'relative_time': 'Time (seconds from start)',
                         'n_bytes': 'Message Size (bytes)',
                         'messageType_readable': 'Message Type/Subtype'
                     },
                     hover_data={
                         'relative_time': ':.2f',
                         'n_bytes': True,
                         'messageType': True,
                         'messageSubtype': True
                     },
                     hover_name='messageType_readable')

    # Customize the layout for better readability
    fig.update_layout(
        xaxis_title='Time Elapsed (seconds)',
        yaxis_title='Message Size (bytes)',
        legend_title='Message Types/Subtypes',
        title={
            'text': 'Network Message Analysis: Received Messages Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica', size=20, color='black')
        },
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.9)'
        ),
        plot_bgcolor='white',
        width=1000,
        height=600
    )

    # Customize the markers - make them larger and more visible
    fig.update_traces(
        marker=dict(
            size=14,  # Larger balls
            opacity=0.8,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )

    # Customize axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    # Show the plot
    fig.show()

if __name__ == '__main__':
    app_init_df,app_inference_df,message_continuous_df = get_dfs()

    # with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.width', None,'display.max_colwidth', None):
    #      print(app_init_df)
    #      print(app_inference_df)
    #      print(message_continuous_df)

    plot_scatter_message_readable(message_continuous_df)
    plot_scatter_message_continuous2(message_continuous_df)



