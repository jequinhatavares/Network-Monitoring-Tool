import os

import pandas as pd
import plotly.express as px
import json
import plotly
import plotly.colors as pc


import plotly.graph_objects as go
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

    return join_times_df, parent_recovery_df, message_interval_df, message_continuous_df


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
        'init_time': "#d7377e",  # Plotly blue
        'search_time': "#64d3f6",  # Plotly orange
        'join_time': "#b8f193"  # Plotly green
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
        fig.update_xaxes(title_font=dict(family='Helvetica', size=14),
                         tickfont=dict(family='Helvetica', size=12) )
        fig.update_yaxes(title_font=dict(family='Helvetica', size=14),
                         tickfont=dict(family='Helvetica', size=12),
                         showgrid=True, gridcolor='lightgray', gridwidth=1,)

        figures[device] = fig

    return figures




def stacked_bar_plot_integration_time(df: pd.DataFrame):
    states = ['init_time', 'search_time', 'join_time']
    state_labels = {
        'init_time': 'Init State',
        'search_time': 'Search State',
        'join_time': 'Join State'
    }

    state_colors = {
        'init_time': "#d7377e",  # Plotly blue
        'search_time': "#64d3f6",  # Plotly orange
        'join_time': "#b8f193"  # Plotly green
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
            textfont=dict(color='black', weight='bold', size=12),  # Black text for better contrast
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
            'text': 'Network Integration Time Breakdown by Device',
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
            font=dict(family='Helvetica', size=12),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    # Clean axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12)
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
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
            font=dict(family='Helvetica', size=12, weight='bold', color='black'),
            yshift=5  # Additional shift for extra spacing
        )
    fig.show()

def parent_recovery_bar_plot(df: pd.DataFrame):
    # Calculate mean recovery time by device type
    # Convert milliseconds to seconds
    df['parent_recovery_time'] = df['parent_recovery_time'] / 1000

    mean_df = df.groupby('type')['parent_recovery_time'].mean().reset_index()

    # Define the desired order
    desired_order = ['ESP8266', 'ESP32', 'RPI']

    # Convert 'type' to categorical with specified order
    mean_df['type'] = pd.Categorical(mean_df['type'], categories=desired_order, ordered=True)

    # Sort the DataFrame by the categorical order
    mean_df = mean_df.sort_values('type')

    # Create bar plot
    fig = px.bar(mean_df,
                 x='type',
                 y='parent_recovery_time',
                 color='type',  # Use Plotly's default colors
                 template="plotly_white",)


    # Add bold annotations with specific size
    for i, row in enumerate(mean_df.itertuples()):
        fig.add_annotation(
            x=row.type,
            y=row.parent_recovery_time,
            text=f"<b>{row.parent_recovery_time:.2f}s</b>",  # Bold text using HTML tags
            showarrow=False,
            yshift=10,
            font=dict(
                family='Helvetica',
                size=12,  # Specific size
                color='black'
            ),
            bgcolor='white',
        )

    # Update layout with Helvetica font
    fig.update_layout(
        title={
            'text': 'Mean Parent Recovery Time by Device Type',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(family='Helvetica', size=20, color='black')
        },
        font_family='Helvetica',
        title_font_family='Helvetica',
        xaxis_title='Device',
        yaxis_title='Mean Parent Recovery Time (s)',
        showlegend=False  # Remove legend since colors are self-explanatory
    )

    # Clean axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12)
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray'
    )

    fig.show()

if __name__ == '__main__':
    join_times_df, parent_recovery_df, message_interval_df, message_continuous_df = get_dfs()

    with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.width', None,'display.max_colwidth', None):
        print(join_times_df)
        print(parent_recovery_df)
        print(message_interval_df)
        print(message_continuous_df)

    #figures = plot_bar_states_mean_pdevice(join_times_df)

    # Show per device
    #figures["ESP8266"].show()
    # figures["ESP32"].show()
    # figures["RPI"].show()
    #stacked_bar_plot_integration_time(join_times_df)

    parent_recovery_bar_plot(parent_recovery_df)
