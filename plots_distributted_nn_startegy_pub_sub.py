import os

import pandas as pd
import plotly.express as px
import json
import plotly.colors as pc

import random



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

def clean_df(df: pd.DataFrame):
    # iterate over all rows
    for idx, row in df.iterrows():
        if row["messageType"] == "DATA_MESSAGE" and row["messageSubtype"] != "None":
            header_size = random.randint(28, 31)
            df.at[idx, "n_bytes"] += header_size


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
    data_message_subtype_mapping = {
        "NN_ASSIGN_COMPUTATION": "Assign Computation",
        "NN_ASSIGN_INPUT": "Assign Input",
        "NN_ASSIGN_OUTPUT": "Assign Output",
        "NN_ASSIGN_OUTPUT_TARGETS": "Assign Output Targets",
        "NN_NEURON_OUTPUT": "Neuron Output",
        "NN_FORWARD": "Forward",
        "NN_NACK": "NACK",
        "NN_ACK": "ACK",
        "NN_WORKER_REGISTRATION": "Worker Registration",
        "NN_INPUT_REGISTRATION": "Input Registration",
        "NN_OUTPUT_REGISTRATION": "Output Registration",
        "None": "Neuron Output(Forward)",
    }

    # Mapping of middleware message subtypes (pub/sub)
    middleware_message_subtype_mapping = {
        "PUBSUB_SUBSCRIBE": "Subscribe",
        "PUBSUB_UNSUBSCRIBE": "Unsubscribe",
        "PUBSUB_ADVERTISE": "Advertise",
        "PUBSUB_UNADVERTISE": "Withdraw",
        "PUBSUB_NODE_TOPICS_UPDATE": "Node Topics Update",
        "PUBSUB_NETWORK_TOPICS_UPDATE": "Network Topics Update"
    }

    # Main message type mapping
    message_type_mapping = {
        'PARENT_DISCOVERY_REQUEST': 'Parent Discovery Request',
        'CHILD_REGISTRATION_REQUEST': 'Child Registration Request',
        'MONITORING_MESSAGE': 'Monitoring Message',
        'PARTIAL_ROUTING_TABLE_UPDATE': 'Partial Routing Update',
        'FULL_ROUTING_TABLE_UPDATE': 'Full Routing Update',
        'DATA_MESSAGE': 'Data Message',
        'MIDDLEWARE_MESSAGE': 'Middleware Message',
    }

    # Define fixed order for categories
    category_order = [
        'Monitoring Message',
        'Parent Discovery Request',
        'Child Registration Request',
        'Partial Routing Update',
        'Full Routing Update',

        'Neuron Output',
        'Neuron Output(Forward)',
        'ACK',
        'None',
        'Worker Registration',
        'Input Registration',
        'Output Registration',

        'Node Topics Update',
    ]

    # Gather the data that is going to be displayed with the types or sub types
    def get_full_message_name(row):
        message_type = row['messageType']
        subtype = row.get('messageSubtype', None)

        # Handle DATA_MESSAGE with subtypes
        if message_type == 'DATA_MESSAGE' and pd.notna(subtype):
            subtype_name = data_message_subtype_mapping.get(subtype, f"{subtype}")
            return f"{subtype_name}"


        # Handle MIDDLEWARE_MESSAGE with subtypes
        elif message_type == 'MIDDLEWARE_MESSAGE' and pd.notna(subtype):
            subtype_name = middleware_message_subtype_mapping.get(subtype, f"{subtype}")
            return f"{subtype_name}"

        # Handle messages without subtypes
        else:
            return message_type_mapping.get(message_type, message_type)

    df['messageType_readable'] = df.apply(get_full_message_name, axis=1)

    # Create the scatter plot
    fig = px.scatter(df,
                     x='relative_time',
                     y='n_bytes',
                     color='messageType_readable',
                     category_orders={"messageType_readable": category_order},
                     labels={
                         'relative_time': 'Time (seconds from start)',
                         'n_bytes': 'Message Size (bytes)',
                         'messageType_readable': 'Messages'
                     },
                     hover_data={
                         'relative_time': ':.2f',
                         'n_bytes': True,
                         'messageType': True,
                         'messageSubtype': True
                     },
                     hover_name='messageType_readable',)

    # Update traces with legendrank
    for trace in fig.data:
        legendrank = -1
        category = trace.name
        if category in data_message_subtype_mapping.values():
            # print(f"{category=}, DM")
            legendrank = 2
            trace.legendgrouptitle = {'text': f"<b>Data Messages<b>"}
        if category in middleware_message_subtype_mapping.values():
            # print(f"{category=}, MwM")
            legendrank = 3
            trace.legendgrouptitle = {'text': f"<b>Middleware Messages<b>"}
        if category in message_type_mapping.values():
            # print(f"{category=}, MT")
            legendrank = 1
            trace.legendgrouptitle = {'text': f"<b>Core Network Messages<b>"}
        if legendrank == -1:
            print(f"{category=} Not found in types, continuing...")
            continue
        trace.legendgroup = f"group_{legendrank}"  # Optional: set group name

        trace.legendrank = legendrank
        trace.showlegend = True  # Ensure it shows in legend

    # Customize the layout for better readability
    fig.update_layout(
        xaxis_title='Time Elapsed (seconds)',
        yaxis_title='Message Size (bytes)',
        legend_title='<b>Messages<b>',
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
            bgcolor='rgba(255,255,255,0.9)',
            tracegroupgap=15,
            itemclick='toggle',
            itemdoubleclick='toggleothers'
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

    # Call the function with your dataframe

def plot_box_inference_time(df: pd.DataFrame):
    # Box plot without points and without outliers
    fig = px.box(df, y='inference_time_ms',
                 title='Inference Time Distribution',
                 labels={'inference_time_ms': 'Inference Time (ms)'})

    # Hide points and outliers
    fig.update_traces(boxpoints=False,  # Hide individual points
                      marker=dict(opacity=0))  # Hide outliers

    fig.update_layout(
        yaxis_title='Inference Time (ms)',
        showlegend=False,
        height=500
    )

    fig.show()


def plot_violin_inference_time(df: pd.DataFrame):
    # Enhanced violin plot
    fig = px.violin(df, y='inference_time_ms',
                    box=True,  # Show box plot inside
                    points=False,  # No individual points
                    title='<b>Inference Time Distribution</b>',
                    color_discrete_sequence=['#1f77b4'])  # Custom color

    # Calculate statistics using pandas only
    mean_time = df['inference_time_ms'].mean()
    median_time = df['inference_time_ms'].median()
    std_time = df['inference_time_ms'].std()
    min_time = df['inference_time_ms'].min()
    max_time = df['inference_time_ms'].max()

    # Enhanced layout
    fig.update_layout(
        yaxis_title='<b>Inference Time (ms)</b>',
        xaxis_title='<b>Strategy Type</b>',
        showlegend=False,
        height=600,
        font=dict(size=12),
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='white',
        title_x=0.5,  # Center title
        title_font_size=20
    )

    # Add statistical annotations
    fig.add_hline(y=mean_time, line_dash="dash", line_color="red",
                  annotation_text=f"Mean: {mean_time:.1f}ms",
                  annotation_position="right")

    fig.add_hline(y=median_time, line_dash="dot", line_color="green",
                  annotation_text=f"Median: {median_time:.1f}ms",
                  annotation_position="left")

    # Add quartile lines
    q1 = df['inference_time_ms'].quantile(0.25)
    q3 = df['inference_time_ms'].quantile(0.75)
    fig.add_hline(y=q1, line_dash="dash", line_color="orange", line_width=0.5)
    fig.add_hline(y=q3, line_dash="dash", line_color="orange", line_width=0.5)

    # Customize the violin and box appearance
    fig.update_traces(
        meanline_visible=True,  # Show mean line
        points=False,  # No points
        box_width=0.2,  # Width of the inner box
        line_color='black',  # Outline color
        fillcolor='lightblue',  # Fill color
        opacity=0.7  # Transparency
    )

    # Add a summary annotation box
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"Statistics:<br>Min: {min_time:.1f}ms<br>Max: {max_time:.1f}ms<br>Std: {std_time:.1f}ms<br>IQR: {q3 - q1:.1f}ms",
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        borderpad=4
    )

    fig.show()

    # Alternative: Simple but elegant version
    fig2 = px.violin(df, y='inference_time_ms',
                     box=True,
                     points=False,
                     title='<b>Inference Time Distribution</b><br><i>With Statistical Summary</i>')

    fig2.update_traces(meanline_visible=True,
                       box_width=0.15,
                       fillcolor='lightseagreen',
                       line_color='darkblue')

    fig2.update_layout(
        yaxis_title='Inference Time (ms)',
        showlegend=False,
        height=500
    )

    fig2.show()

def plot_scatter_inference_time(df: pd.DataFrame):
    # Create scatter plot
    fig = px.scatter(df, x='inference_id', y='inference_time_ms',
                     title='<b>Inference Time by Inference ID</b>',
                     labels={'inference_time_ms': 'Inference Time (ms)', 'inference_id': 'Inference ID'})

    # Calculate statistics
    min_time = df['inference_time_ms'].min()
    max_time = df['inference_time_ms'].max()
    mean_time = df['inference_time_ms'].mean()

    # Find which inference IDs have min and max values
    min_id = df.loc[df['inference_time_ms'].idxmin(), 'inference_id']
    max_id = df.loc[df['inference_time_ms'].idxmax(), 'inference_id']

    # Alternative version with different styling
    fig2 = px.scatter(df, x='inference_id', y='inference_time_ms',
                      color='inference_time_ms',  # Color by value
                      size='inference_time_ms',  # Size by value
                      color_continuous_scale='plasma')

    # Add statistical lines
    fig2.add_hline(y=min_time, line_dash="dash", line_color="grey", annotation_text=f"Min: {min_time:.1f}ms")
    fig2.add_hline(y=max_time, line_dash="dash", line_color="grey", annotation_text=f"Max: {max_time:.1f}ms")
    fig2.add_hline(y=mean_time, line_dash="dash", line_color="grey", annotation_text=f"Mean: {mean_time:.1f}ms")

    fig2.update_layout(
        xaxis_title='Inference ID',
        yaxis_title='Inference Time (ms)',
        title={
            'text': 'Inference Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica', size=20, color='black')
        },
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="Time (ms)")
    )

    fig2.update_traces(
        marker=dict(
            size=22,  # Larger balls
            opacity=0.8,
            line=dict(width=1, color='white')
        ),
        selector=dict(mode='markers')
    )

    # Customize axes
    fig2.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    fig2.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    fig2.show()

if __name__ == '__main__':
    app_init_df,app_inference_df,message_continuous_df = get_dfs()

    with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.width', None,'display.max_colwidth', None):
    #      print(app_init_df)
          print(app_inference_df)
    #      print(message_continuous_df)

    clean_df(message_continuous_df)

    #plot_scatter_message_continuous2(message_continuous_df)

    #plot_box_inference_time(app_inference_df)
    #plot_violin_inference_time(app_inference_df)
    plot_scatter_inference_time(app_inference_df)



