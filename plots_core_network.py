import os

import pandas as pd
import plotly.express as px
import json
import plotly
import plotly.colors as pc

from app_common import *
from unused_plots import *

import plotly.graph_objects as go
from networkx.algorithms.bipartite.basic import color
from plotly.subplots import make_subplots

# Device color mapping
device_colors = {
    "ESP8266": "#64D3F6",
    "ESP32": "#B8F193",
    "RPI": "#D7377E"
}


def get_dfs():
    runs = []
    for root, dirs, files in os.walk("logs"):
        for file in files:
            if file.startswith('run-join'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    runs += json.load(f)
    join_times_df = pd.DataFrame(runs)
    join_times_df = join_times_df.astype(
        {'init_time': 'int32', 'search_time': 'int32', 'join_time': 'int32', 'type': 'str'})

    runs = []

    for root, dirs, files in os.walk("logs"):
        for file in files:
            if file.startswith('run-parent-recovery'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    runs += json.load(f)
    parent_recovery_df = pd.DataFrame(runs)
    parent_recovery_df = parent_recovery_df.astype({'parent_recovery_time': 'int32', 'type': 'str'})

    runs = []
    for root, dirs, files in os.walk("logs"):
        for file in files:
            if file.startswith('run-messages'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    runs += json.load(f)
    message_interval_df = pd.DataFrame(runs)
    message_interval_df = message_interval_df.astype(
        {'type': 'str', 'node_ip': 'str', 'monitoring_time': 'int32', 'routing_msg_count': 'int32',
         'routing_bytes_count': 'int32', 'lifecycle_msg_count': 'int32',
         'lifecycle_bytes_count': 'int32', 'middleware_msg_count': 'int32',
         'middleware_bytes_count': 'int32', 'app_msg_count': 'int32',
         'app_bytes_count': 'int32', 'monitoring_msg_count': 'int32',
         'monitoring_bytes_count': 'int32'})

    runs = []
    with open('logs/core_network/run-continuous-messages-0.json', 'r') as f:
        runs += json.load(f)
    message_continuous_df = pd.DataFrame(runs)
    message_continuous_df = message_continuous_df.astype(
        {'timestamp': 'float64', 'messageType': 'str', 'strategyType': 'str', 'messageSubtype': 'str',
         'n_bytes': 'int32'})
    # Filter rows within the first 607.61 seconds
    start_time = message_continuous_df['timestamp'].min()
    message_continuous_df_filter = message_continuous_df[
        message_continuous_df['timestamp'] - start_time <= max_continuous_sample]

    runs = []
    for file in ['logs/core_network/' + "/" + f for f in os.listdir('logs/core_network/') if f.startswith('run-end-to-end-delay')]:
        with open(file, 'r') as f:
            runs += json.load(f)
    delay_df = pd.DataFrame(runs)
    delay_df = delay_df.astype({'node_ip': 'str', 'latency': 'int32', 'hop_count': 'int32'})

    return join_times_df, parent_recovery_df, message_interval_df, message_continuous_df,message_continuous_df_filter,delay_df




def plot_bar_states_mean_pdevice(df):
    """
        Create a separate bar plot for each device showing the mean time per state.
        """
    figures = {}

    # Reshape dataframe
    df_long = df.melt(id_vars="type", value_vars=["init_time", "search_time", "join_time"],
                      var_name="state", value_name="time")

    # Define the desired order and labels
    state_order = ["init_time", "search_time", "join_time"]
    state_labels = {
        "init_time": "Init",
        "search_time": "Search",
        "join_time": "Join"
    }
    state_colors = {
        'init_time': px.colors.qualitative.Plotly[0],  # Plotly blue
        'search_time': px.colors.qualitative.Plotly[1],  # Plotly orange
        'join_time': px.colors.qualitative.Plotly[2]  # Plotly green
    }


    for device in df_long["type"].unique():
        subset = df_long[df_long["type"] == device]

        # Compute mean per state
        means = subset.groupby("state")["time"].mean().reset_index()

        # Convert to seconds for the y-axis
        means["time_seconds"] = means["time"] / 1000

        # Ensure the desired order and apply human-readable labels
        means["state"] = pd.Categorical(means["state"], categories=state_order, ordered=True)
        means = means.sort_values("state")
        means["state_label"] = means["state"].map(state_labels)

        # Create formatted text annotations - show seconds for larger values, ms for smaller
        def format_time(time_ms):
            if time_ms >= 1000:  # If 1000ms or more, show as seconds with one decimal
                return f"{time_ms / 1000:.1f}s"
            else:  # If less than 1000ms, show as milliseconds
                return f"{time_ms:.0f}ms"

        means["formatted_text"] = means["time"].apply(format_time)

        # Bar plot for mean values (using seconds on y-axis)
        fig = px.bar(
            means,
            x="state_label",
            y="time_seconds",  # Use seconds for y-axis
            color="state",
            color_discrete_map=state_colors,
            title=f"Mean State Times for {device}",
            text=means["formatted_text"]  # Use formatted text for annotations
        )

        # Adjust layout with better title formatting and bold annotations
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=12, weight=1000, family="Helvetica", color='black')
        )


        fig.update_layout(
            yaxis_title="Time (s)",  # Updated to seconds
            xaxis_title="State",
            showlegend=False,
            xaxis={'categoryorder': 'array', 'categoryarray': [state_labels[s] for s in state_order]},
            title={
                'text': f"Mean State Times for {device}",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20, 'family': 'Helvetica', 'color': 'black'}
            },
            plot_bgcolor='white',
            # paper_bgcolor='white',
        )

        # Specifically update axis tick fonts
        fig.update_xaxes(title_font=dict(family='Helvetica', size=16),
                         tickfont=dict(family='Helvetica', size=14,color="Black") )
        fig.update_yaxes(title_font=dict(family='Helvetica', size=16,color="Black"),
                         tickfont=dict(family='Helvetica', size=14,color="Black"),
                         showgrid=True, gridcolor='lightgray', gridwidth=1,)

        figures[device] = fig

    figures["ESP8266"].write_image(
        "images/core_network/init_states_8266.png",
        scale=2  # multiplies the base resolution
    )
    figures["ESP32"].write_image(
        "images/core_network/init_states_32.png",
        scale=2  # multiplies the base resolution
    )
    figures["RPI"].write_image(
        "images/core_network/init_states_rpi.png",
        scale=2  # multiplies the base resolution
    )

    figures["ESP8266"].show()
    return figures


def stacked_bar_plot_integration_time(df: pd.DataFrame):
    states = ['init_time', 'search_time', 'join_time']
    state_labels = {
        'init_time': 'Init State',
        'search_time': 'Search State',
        'join_time': 'Join State'
    }

    state_colors = {
        'init_time': px.colors.qualitative.Plotly[0],  # Plotly blue
        'search_time': px.colors.qualitative.Plotly[1],  # Plotly orange
        'join_time': px.colors.qualitative.Plotly[2]  # Plotly green
    }

    devices = ['ESP8266', 'ESP32', 'RPI']

    # Calculate mean times and percentages
    results = []
    for device in devices:
        device_df = df[df["type"] == device]
        device_means = {}
        total_time = 0

        for state in states:
            mean_time_seconds = device_df[state].mean() / 1000
            device_means[state] = mean_time_seconds
            total_time += mean_time_seconds

        # Calculate percentages
        for state in states:
            device_means[f'{state}_pct'] = (device_means[state] / total_time) * 100

        device_means['device'] = device
        device_means['total_time'] = total_time
        results.append(device_means)

    # Create the stacked bar plot
    fig = go.Figure()

    for state in states:
        state_means = [result[state] for result in results]
        state_percentages = [result[f'{state}_pct'] for result in results]

        # Only show percentage if segment is large enough
        text_annotations = []
        for pct in state_percentages:
            if pct > 5:  # Only show percentage if it's more than 5%
                text_annotations.append(f'{pct:.1f}%')
            else:
                text_annotations.append('')

        fig.add_trace(go.Bar(
            x=devices,
            y=state_means,
            name=state_labels[state],
            marker_color=state_colors[state],
            marker_line=dict(width=2, color='white'),  # Add subtle border for definition
            text=text_annotations,
            textposition='inside',
            textfont=dict(color='black',family='Helvetica', weight='bold', size=12),  # Black text for better contrast
            hovertemplate=(
                    f"<b>{state_labels[state]}</b><br>" +
                    "Time: %{y:.3f}s<br>" +
                    "Percentage: %{customdata:.1f}%<extra></extra>"
            ),
            customdata=state_percentages,
            width=0.8
        ))

    # Clean layout
    fig.update_layout(
        title={
            'text': 'Network Integration Time by Device',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica', size=20, color='black')
        },
        xaxis_title='Device',
        yaxis_title='Time (s)',
        barmode='stack',
        font=dict(family='Helvetica', size=15),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100, b=60, l=60, r=60),  # Increased top margin for higher annotations
        legend=dict(
            font=dict(family='Helvetica', size=16),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    # Clean axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=18,color="Black"),
        tickfont=dict(family='Helvetica', size=16,color="Black")
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=18,color="Black"),
        tickfont=dict(family='Helvetica', size=16,color="Black"),
        gridcolor='lightgray'
    )

    # Total time annotations moved higher up
    for i, device in enumerate(devices):
        total_time = results[i]['total_time']
        fig.add_annotation(
            x=device,
            y=total_time * 1.03,  # Increased from 1.02 to 1.08 - moved higher
            text=f'Total: {total_time:.2f}s',
            showarrow=False,
            font=dict(family='Helvetica', size=15, weight='bold', color='black'),
            yshift=5  # Additional shift for extra spacing
        )
    fig.show()

    fig.write_image(
        "images/core_network/init_device_comparison.png",
        width=761,
        height=599,
        scale=1  # multiplies the base resolution
    )

def parent_recovery_bar_plot(df: pd.DataFrame):
    # Calculate mean recovery time by device type
    # Convert milliseconds to seconds
    df['parent_recovery_time'] = df['parent_recovery_time'] / 1000

    mean_df = df.groupby('type')['parent_recovery_time'].mean().reset_index()

    # Define the desired order
    desired_order = ['ESP8266', 'ESP32', 'RPI']

    # Create bar plot
    fig = px.bar(mean_df,
                 x='type',
                 y='parent_recovery_time',
                 color='type',  # Use Plotly's default colors
                 template="plotly_white",
                 category_orders={"type": desired_order})


    # Add bold annotations with specific size
    for i, row in enumerate(mean_df.itertuples()):
        fig.add_annotation(
            x=row.type,
            y=row.parent_recovery_time,
            text=f"{row.parent_recovery_time:.2f}s",  # Bold text using HTML tags
            showarrow=False,
            yshift=10,
            font=dict(
                family='Helvetica',
                size=15,  # Specific size
                color='black',
                weight='bold',
            ),
        )

    # Update layout with Helvetica font
    fig.update_layout(
        title={
            'text': 'Mean Parent Recovery Time by Device Type',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica',size=20, color='black')
        },
        font_family='Helvetica',
        title_font_family='Helvetica',
        xaxis_title='Device',
        yaxis_title='Time (s)',
        showlegend=False  # Remove legend since colors are self-explanatory
    )

    # Clean axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=18,color='black'),
        tickfont=dict(family='Helvetica', size=16,color="Black")
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=18,color='black'),
        tickfont=dict(family='Helvetica', size=16,color="Black"),
        gridcolor='lightgray'
    )

    fig.show()
    fig.write_image(
        "images/core_network/parent_recovery_comparison.png",
        width = 761,
        height= 599,
        scale=2  # multiplies the base resolution
    )


def plot_mean_messages(df: pd.DataFrame):
    # Select message-related columns
    msg_cols = [
        "routing_msg_count", "routing_bytes_count",
        "lifecycle_msg_count", "lifecycle_bytes_count",
        "middleware_msg_count", "middleware_bytes_count",
        "app_msg_count", "app_bytes_count",
        "monitoring_msg_count", "monitoring_bytes_count"
    ]

    # Compute mean across all rows
    means = df[msg_cols].mean()

    # Compute bytes/s using monitoring_time (convert to seconds)
    monitoring_time_s = df["monitoring_time"].iloc[0] / 1000.0

    agg = pd.DataFrame({
        "count": [
            means["routing_msg_count"],
            means["lifecycle_msg_count"],
            means["middleware_msg_count"],
            means["app_msg_count"],
            means["monitoring_msg_count"],
        ],
        "bytes": [
            means["routing_bytes_count"],
            means["lifecycle_bytes_count"],
            means["middleware_bytes_count"],
            means["app_bytes_count"],
            means["monitoring_bytes_count"],
        ]
    }, index=["routing", "lifecycle", "middleware", "app", "monitoring"])

    # Add Bytes/s column
    agg["bytes_per_s"] = agg["bytes"] / monitoring_time_s

    agg = agg.reset_index().rename(columns={"index": "message_type"})
    print(agg)

    # Scatter plot: average count vs bytes
    fig_scatter = px.scatter(
        agg,
        x="count",
        y="bytes",
        size="bytes",
        text="message_type",
        color="message_type",
        title="Average Message Count vs Bytes per Type"
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.show()

    # Grouped bar chart: counts, bytes, bytes/s
    fig_bar = go.Figure(data=[
        go.Bar(name="Average Count", x=agg["message_type"], y=agg["count"]),
        go.Bar(name="Average Bytes", x=agg["message_type"], y=agg["bytes"]),
        go.Bar(name="Average Bytes/s", x=agg["message_type"], y=agg["bytes_per_s"])
    ])
    fig_bar.update_layout(
        barmode="group",
        title="Average Messages, Bytes and Bytes/s per Type",
        xaxis_title="Message Type",
        yaxis_title="Average Value"
    )
    fig_bar.show()

    # Pie chart: proportions of average counts
    fig_pie_count = px.pie(
        agg,
        values="count",
        names="message_type",
        title="Proportion of Average Message Counts"
    )
    fig_pie_count.show()

    # Pie chart: proportions of average bytes
    fig_pie_bytes = px.pie(
        agg,
        values="bytes",
        names="message_type",
        title="Proportion of Average Message Bytes"
    )
    fig_pie_bytes.show()


def plot_scatter_message_continuous(df: pd.DataFrame):
    # Convert timestamp to relative seconds (starting from 0)
    first_timestamp = df['timestamp'].iloc[0]
    df['relative_time'] = df['timestamp'] - first_timestamp

    # Create human-readable message type labels
    message_type_mapping = {
        'PARENT_DISCOVERY_REQUEST': 'Parent Discovery Request',
        'CHILD_REGISTRATION_REQUEST': 'Child Registration Request',
        'MONITORING_MESSAGE': 'Monitoring Message',
        'PARTIAL_ROUTING_TABLE_UPDATE': 'Partial Routing Update',
        'FULL_ROUTING_TABLE_UPDATE': 'Full Routing Update'
    }

    # Define fixed order for categories
    category_order = [
        'Monitoring Message',
        'Parent Discovery Request',
        'Child Registration Request',
        'Partial Routing Update',
        'Full Routing Update',
    ]

    df['messageType_readable'] = df['messageType'].map(message_type_mapping)

    # Create the scatter plot
    fig = px.scatter(df,
                     x='relative_time',
                     y='n_bytes',
                     color='messageType_readable',
                     title='',
                     category_orders={"messageType_readable": category_order},
                     labels={
                         'relative_time': 'Time (seconds from start)',
                         'n_bytes': 'Message Size (bytes)',
                         'messageType_readable': 'Message Type'
                     },
                     hover_data={
                         'relative_time': ':.2f',
                         'n_bytes': True,
                         'messageType_readable': True
                     },
                     hover_name='messageType_readable')

    # Customize the layout for better readability
    fig.update_layout(
        xaxis_title='Time Elapsed (seconds)',
        yaxis_title='Message Size (bytes)',
        legend_title='Message Types',
        title={
            'text': 'Received Messages Over Time',
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
            size=15,  # Larger balls
            opacity=0.9,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )

    # Customize axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=16,color="Black"),
        tickfont=dict(family='Helvetica', size=14,color="Black"),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=16,color="Black"),
        tickfont=dict(family='Helvetica', size=14,color="Black"),
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )


    # Show the plot
    fig.show()
    fig.write_image(
        "images/core_network/messages_root.png",
        width=1000,
        height=600,
        scale=4  # multiplies the base resolution
    )


def calculate_mean_delay(df: pd.DataFrame):
    hop_count_sum = df["hop_count"].values.sum()
    latency_sum = df["latency"].values.sum()
    mean_latency = latency_sum/hop_count_sum

    min_latency = df.min(axis=0)["latency_per_hop"]
    max_latency = df.max(axis=0)["latency_per_hop"]

    df["latency_per_hop"] = df["latency"] / df["hop_count"]

    # Helper functions
    def mean_absolute_deviation(x):
        m = x.mean()
        return (x.sub(m).abs().mean())

    def percentile(x, p):
        return x.quantile(p / 100.0)

    def outlier_ratio(x):
        m = x.mean()
        s = x.std()
        if s == 0 or pd.isna(s):
            return 0.0
        return (x > m + 2 * s).mean()

    #print(df.head())


    # Boxplot: distribution of latency per hop count
    fig_box = px.box(
        df,
        x="hop_count",
        y="latency",
        points="all",  # shows all data points
        hover_data=["node_ip"],
        title="Latency distribution per hop count"
    )
    fig_box.show()

    # Group by hop_count and calculate key statistics
    summary = df.groupby("hop_count").agg(
        mean_latency=("latency", "mean"),
        std_latency=("latency", "std"),
        jitter=("latency", mean_absolute_deviation),
        p95_latency=("latency", lambda x: percentile(x, 95)),
        count=("latency", "count"),
        outlier_ratio=("latency", outlier_ratio)
    ).reset_index()

    print("=== Summary table ===")
    print(summary)



if __name__ == '__main__':
    join_times_df, parent_recovery_df, message_interval_df, message_continuous_df,message_continuous_df_filter,delay_df= get_dfs()

    #with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.width', None,'display.max_colwidth', None):
    #     print(join_times_df)
    #     print(parent_recovery_df)
    #     print(message_interval_df)
    #     print(message_continuous_df)
    #     print(delay_df)

    type_counts = join_times_df['type'].value_counts()
    print("Device Type Init State Counts:")
    print("===================")
    for device_type, count in type_counts.items():
        print(f"{device_type}: {count} occurrences")

    recovery_counts = parent_recovery_df['type'].value_counts()
    print("Device Type Parent Recovery State Counts:")
    print("===================")
    for device_type, count in recovery_counts.items():
        print(f"{device_type}: {count} occurrences")

    delay_count = delay_df['hop_count'].value_counts()
    print("RTT Samples by Hop Count:")
    print("===================")
    for n_hops, count in delay_count.items():
        print(f"{n_hops}: {count} occurrences")

    #figures = plot_bar_states_mean_pdevice(join_times_df)

    # # Show per device
    # figures["ESP8266"].show()
    # figures["ESP32"].show()
    # figures["RPI"].show()
    #stacked_bar_plot_integration_time(join_times_df)

    #parent_recovery_bar_plot(parent_recovery_df)

    #plot_mean_messages(message_interval_df)

    #plot_scatter_message_continuous(message_continuous_df)

    #calculate_mean_delay(delay_df)

    #analyze_message_metrics(message_continuous_df_filter)

    #box_plot_with_3_devices_by_state(join_times_df)

    violin_plot_with_3_devices_by_two_states(join_times_df)

    #box_plot_parent_recovery_by_device(parent_recovery_df)

    violin_plot_parent_recovery_by_device_annotations(parent_recovery_df)


