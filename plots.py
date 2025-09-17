import os

import pandas as pd
import plotly.express as px
import json
import plotly

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_dfs():
    runs = []
    for file in ["logs/"+f for f in os.listdir("logs") if f.startswith('run-join')]:
        with open(file,'r') as f:
            runs += json.load(f)
    df = pd.DataFrame(runs)
    df = df.astype({'init_time': 'int32','search_time': 'int32','join_time': 'int32','type': 'str'})

    runs2 = []
    for file in ["logs/"+f for f in os.listdir("logs") if f.startswith('run-messages')]:
        with open(file,'r') as f:
            runs2 += json.load(f)
    df2 = pd.DataFrame(runs2)
    df2 = df2.astype({'routing_messages': 'int32','lifecycle_messages': 'int32','middleware_messages': 'int32','type': 'str'})


    return df,df2

# Define custom colours for each device
device_colors = {
    "ESP8266": "#FF851B",  # orange
    "ESP32": "#3D9970",  # green
    "RaspberryPi": "#FF4136"  # red
}

def plot_violin(df: pd.DataFrame):
    # Melt the DataFrame to long format for plotting
    df_melted = df.melt(id_vars=['type'],
                        value_vars=['init_time', 'search_time', 'join_time'],
                        var_name='time_type',
                        value_name='time_value')

    # Create violin plot
    fig = px.violin(df_melted,
                    x='time_type',
                    y='time_value',
                    color='time_type',
                    box=True,  # Show box plot inside violin
                    points='all',  # Show all points
                    title='Time Distribution by Type',
                    labels={'time_type': 'Time Type', 'time_value': 'Time (units)'})

    # Customize layout
    fig.update_layout(
        xaxis_title='Time Type',
        yaxis_title='Time Value',
        showlegend=False
    )

    # Show plot
    fig.show()

def box_plot(df: pd.DataFrame):
    # Create a figure with subplots to show both box and individual points
    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=('Init Time', 'Search Time', 'Join Time'),
                        shared_yaxes=True)

    # Add box plots
    fig.add_trace(go.Box(y=df['init_time'], name='Init Time', boxpoints='all', jitter=0.3), 1, 1)
    fig.add_trace(go.Box(y=df['search_time'], name='Search Time', boxpoints='all', jitter=0.3), 1, 2)
    fig.add_trace(go.Box(y=df['join_time'], name='Join Time', boxpoints='all', jitter=0.3), 1, 3)

    # Update layout
    fig.update_layout(
        title='Time Measurements for ESP32',
        yaxis_title='Time (units)',
        showlegend=False,
        height=500
    )

    # Show plot
    fig.show()


def box_plot_2(df: pd.DataFrame):
    # Reshape dataframe into long format
    df_long = df.melt(id_vars=["type"],
                      value_vars=["init_time", "search_time", "join_time"],
                      var_name="state",
                      value_name="time")

    # Create box plot
    fig = px.box(df_long, x="state", y="time", color="state",
                 title="Box plot of times by state")

    fig.show()



def box_plot_with_3_devices(df: pd.DataFrame):
    # Convert to long format
    df_long = df.melt(id_vars=["type"],
                      value_vars=["init_time", "search_time", "join_time"],
                      var_name="state",
                      value_name="time")

    # Create subplots
    fig = make_subplots(rows=1, cols=3, subplot_titles=["ESP8266","ESP32", "RaspberryPi"])

    device_order = ["ESP8266","ESP32", "RaspberryPi"]
    state_order = ["init_time", "search_time", "join_time"]


    for i, device in enumerate(device_order, start=1):
        sub_df = df_long[df_long["type"] == device]
        box = px.box(
            sub_df,
            x="state",
            y="time",
            category_orders={"state": state_order},
            color_discrete_sequence=[device_colors[device]])
        for trace in box.data:
            fig.add_trace(trace, row=1, col=i)

    # Update layout for readability
    fig.update_layout(title_text="Device times by state (separate axes)",
                      showlegend=False)

    fig.show()


def box_plot_with_3_devices_by_state(df: pd.DataFrame):
    states = ['init_time', 'search_time', 'join_time']
    devices = ['ESP8266', 'ESP32', 'RaspberryPi']

    # Create subplots
    fig = make_subplots(rows=1, cols=3, subplot_titles=states)

    for i, state in enumerate(states, start=1):
        for j, device in enumerate(devices):
            sub_df = df[df["type"] == device]
            fig.add_trace(go.Box(
                y=sub_df[state],
                name=device,
                marker_color=device_colors[device],
                width=0.4,  # make boxes wider
                offsetgroup=j,  # group boxes side by side
                showlegend=(i == 1)  # legend only in first subplot
            ), row=1, col=i)

    # Layout
    fig.update_layout(
        yaxis_title='Time (ms)',
        yaxis2_title='Time (ms)',
        yaxis3_title='Time (ms)',
        boxmode='group',  # group boxes
        title='Device times per state (each state has its own subplot)'
    )

    fig.show()



def bar_plot_message_per_layer(df: pd.DataFrame):
    # Compute mean per layer
    means = df[["routing_messages", "lifecycle_messages", "middleware_messages"]].mean().reset_index()
    means.columns = ["layer", "mean_count"]

    # Round values for display
    means["mean_count"] = means["mean_count"].round(0).astype(int)


    # Bar plot with different colours
    fig = px.bar(
        means,
        x="layer",
        y="mean_count",
        text="mean_count",
        color="layer",
        color_discrete_map=device_colors,
        title="Average number of messages per layer (across devices)"
    )

    # Improve text position and formatting
    fig.update_traces(textposition="outside")

    # Layout polish
    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        xaxis_title="Layer",
        yaxis_title="Average messages",
        showlegend=False
    )

    fig.show()

if __name__ == '__main__':
    df,df2 = get_dfs()
    #print(df.head())
    #print(df2.head())
    plot_violin(df)
    box_plot(df)
    box_plot_2(df)
    box_plot_with_3_devices(df)

    box_plot_with_3_devices_by_state(df)

    bar_plot_message_per_layer(df2)


