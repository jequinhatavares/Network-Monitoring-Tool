import os

import pandas as pd
import plotly.express as px
import json
import plotly

import plotly.graph_objects as go
from plotly.subplots import make_subplots



def get_df():
    runs = []
    for file in ["logs/"+f for f in os.listdir("logs") if f.startswith('run-join')]:
        with open(file,'r') as f:
            runs += json.load(f)
    df = pd.DataFrame(runs)
    df = df.astype({'init_time': 'int32','search_time': 'int32','join_time': 'int32','type': 'str'})

    return df

def plot_violin(df: pd.DataFrame):
    # Melt the DataFrame to long format for plotting
    df_melted = df.melt(id_vars=['type'],
                        value_vars=['init_time', 'search_time', 'join_time'],
                        var_name='time_type',
                        value_name='time_value')

    print(df_melted)

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

def box_plot_log(df: pd.DataFrame):
    df_melted = df.melt(id_vars=["type"],
            value_vars=["init_time", "search_time", "join_time"],
            var_name="state",
            value_name="time")
    # Create box plot with logarithmic y-axis
    fig = px.box(df_melted,
                 x='state',
                 y='time',
                 color='state',
                 title='Time Measurements for ESP32 (Log Scale)',
                 labels={'time_type': 'Time Type', 'time_value': 'Time (units, log scale)'})

    # Set y-axis to logarithmic scale
    fig.update_layout(yaxis_type="log")

    # Add mean markers
    for i, time_type in enumerate(['init_time', 'search_time', 'join_time']):
        mean_val = df[time_type].mean()
        fig.add_annotation(
            x=i,
            y=mean_val,
            text=f"Mean: {mean_val:.1f}",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40
        )

    # Show plot
    fig.show()


if __name__ == '__main__':
    df = get_df()
    print(df.head())
    print(df.dtypes)
    plot_violin(df)
    box_plot(df)
    box_plot_2(df)
    box_plot_log(df)

