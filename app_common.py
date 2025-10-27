import os

import pandas as pd
import plotly.express as px
import json

import random
import plotly.graph_objects as go
import re
import math

from networkx.algorithms.bipartite.basic import color

from plotly.colors import qualitative

max_continuous_sample = 607.61

def get_dfs(directory: str, n: int):
    runs = []
    for file in [directory + "/" + f for f in os.listdir(directory) if f.startswith('run-app-init')]:
        with open(file, 'r') as f:
            runs += json.load(f)
    app_init_df = pd.DataFrame(runs)
    app_init_df = app_init_df.astype({'setup_time_ms': 'int32', 'missing_acks': 'int32'})

    runs = []
    files = [directory + "/" + f for f in os.listdir(directory) if f.startswith('run-app-inference')]
    files.sort(key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)])

    for file in files:
        with open(file, 'r') as f:
            runs += json.load(f)

    app_inference_df = pd.DataFrame(runs)
    app_inference_df = app_inference_df.astype({
        'strategy_type': 'str',
        'inference_id': 'int32',
        'inference_time_ms': 'int32',
        'nack_count': 'int32'
    })
    runs = []

    with open(f'{directory}/run-continuous-messages-{n}.json', 'r') as f:
        runs += json.load(f)
    message_continuous_df = pd.DataFrame(runs)
    message_continuous_df = message_continuous_df.astype(
        {'timestamp': 'float64', 'messageType': 'str', 'strategyType': 'str', 'messageSubtype': 'str',
         'n_bytes': 'int32'})

    # print("Min timestamp:", message_continuous_df['timestamp'].min())
    # print("Max timestamp:", message_continuous_df['timestamp'].max())
    # print("Data types:\n", message_continuous_df.dtypes)
    # print("Number of rows before filter:", len(message_continuous_df))

    # Filter rows within the first 607.61 seconds
    start_time = message_continuous_df['timestamp'].min()
    message_continuous_df_filter = message_continuous_df[message_continuous_df['timestamp'] - start_time <= max_continuous_sample]

    # print("Number of rows after filter:", len(message_continuous_df_filter))
    # print("Max elapsed time after filter:", (message_continuous_df_filter['timestamp'] - start_time).max())


    return app_init_df, app_inference_df, message_continuous_df_filter


def clean_df(df: pd.DataFrame):
    # iterate over all rows
    for idx, row in df.iterrows():
        if row["messageType"] == "DATA_MESSAGE" and row["messageSubtype"] != "None":
            header_size = random.randint(28, 31)
            df.at[idx, "n_bytes"] += header_size


def \
        plot_scatter_inference_time(df: pd.DataFrame, save_path: str, show_plot=False):
    # Create a subset with the first 50 rows
    #df_subset = df.head(50).reset_index(drop=True)
    df_subset = df

    # Calculate statistics for this subset
    min_time = df_subset['inference_time_ms'].min()
    max_time = df_subset['inference_time_ms'].max()
    mean_time = df_subset['inference_time_ms'].mean()

    # Find which inference IDs have min and max values
    min_id = df_subset.loc[df_subset['inference_time_ms'].idxmin(), 'inference_id']
    max_id = df_subset.loc[df_subset['inference_time_ms'].idxmax(), 'inference_id']

    # Create scatter plot
    fig2 = px.scatter(
        df_subset,
        x = df_subset.index,
        y = 'inference_time_ms',
        color='inference_time_ms',
        size='inference_time_ms',
        color_continuous_scale='plasma'
    )

    # Add statistical lines
    fig2.add_hline(
        y=min_time, line_dash="dash", line_color="grey",
        annotation=dict(
            text=f"Min: {min_time:.1f} ms",
            font=dict(size=16, family="Helvetica", color="Black"),
            align="left")
    )
    fig2.add_hline(
        y=max_time, line_dash="dash", line_color="grey",
        annotation=dict(
            text=f"Max: {max_time:.1f} ms",
            font=dict(size=16, family="Helvetica", color="Black"),
            align="left")
    )
    fig2.add_hline(
        y=mean_time, line_dash="dash", line_color="grey",
        annotation=dict(
            text=f"Mean: {mean_time:.1f} ms",
            font=dict(size=16, family="Helvetica", color="Black"),
            align="left")
    )

    # Add vertical lines separating different runs
    run_start_indices = df_subset.index[df_subset['inference_id'] == 1].tolist()

    for idx in run_start_indices:
        if idx != 0:  # skip first run start
            fig2.add_vline(
                x=idx,
                line_dash="dash",
                line_color="grey",
                opacity=1,
            )

    # Layout and styling
    fig2.update_layout(
        xaxis_title='Inference ID',
        yaxis_title='Inference Duration (ms)',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="Time (ms)")
    )

    fig2.update_traces(
        marker=dict(size=20, opacity=0.6, line=dict(width=1, color='white')),
        selector=dict(mode='markers')
    )

    # fig2.update_xaxes(
    #     title_font=dict(family='Helvetica', size=18, color="Black"),
    #     tickfont=dict(family='Helvetica', size=16, color="Black"),
    #     gridcolor='lightgray', griddash='dash', showgrid=True
    # )

    fig2.update_yaxes(
        title_font=dict(family='Helvetica', size=18, color="Black"),
        tickfont=dict(family='Helvetica', size=16, color="Black"),
        gridcolor='lightgray', griddash='dash', showgrid=True
    )

    if show_plot:
        fig2.show()

    fig2.write_image(save_path, scale=3)


def analyze_message_metrics(df):
    """
       Analyze messaging metrics from the DataFrame with standard column names
       """

    # Basic validation
    required_cols = ['timestamp', 'messageType', 'strategyType', 'messageSubtype', 'n_bytes']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"  Missing columns: {missing_cols}")
        return None

    # Create a copy to avoid modifying original data
    df_analysis = df.copy()

    # Convert timestamp if needed (assuming Unix timestamp)
    if pd.api.types.is_numeric_dtype(df_analysis['timestamp']):
        df_analysis['datetime'] = pd.to_datetime(df_analysis['timestamp'], unit='s')
    else:
        df_analysis['datetime'] = pd.to_datetime(df_analysis['timestamp'])

    # Calculate time range and duration
    start_time = df_analysis['datetime'].min()
    end_time = df_analysis['datetime'].max()
    #duration_seconds = (end_time - start_time).total_seconds()
    duration_seconds = max_continuous_sample

    # Basic metrics
    total_messages = len(df_analysis)
    total_bytes = df_analysis['n_bytes'].sum()

    # Message type analysis
    message_type_counts = df_analysis['messageType'].value_counts()
    message_type_percentages = (message_type_counts / total_messages * 100)

    # Strategy type analysis
    strategy_counts = df_analysis['strategyType'].value_counts()
    strategy_percentages = (strategy_counts / total_messages * 100)

    # Subtype analysis
    subtype_messages = df_analysis[df_analysis['messageSubtype'].notna()]
    if not subtype_messages.empty:
        subtype_counts = subtype_messages['messageSubtype'].value_counts()
        subtype_percentages = (subtype_counts / len(subtype_messages) * 100)
    else:
        subtype_counts = pd.Series()
        subtype_percentages = pd.Series()

    # Bytes analysis
    bytes_per_second_total = total_bytes / duration_seconds if duration_seconds > 0 else 0
    bytes_by_message_type = df_analysis.groupby('messageType')['n_bytes'].agg(['sum', 'mean', 'count'])
    bytes_by_message_type['bytes_per_second'] = bytes_by_message_type['sum'] / duration_seconds

    # Routing messages analysis
    routing_keywords = ['ROUTING']
    routing_messages = df_analysis[
        df_analysis['messageType'].str.contains('|'.join(routing_keywords), case=False, na=False)]
    total_routing_messages = len(routing_messages)
    routing_percentage = (total_routing_messages / total_messages * 100)
    routing_bytes = routing_messages['n_bytes'].sum()

    # Data messages analysis
    data_keywords = ['DATA']
    data_messages = df_analysis[df_analysis['messageType'].str.contains('|'.join(data_keywords), case=False, na=False)]
    total_data_messages = len(data_messages)
    data_percentage = (total_data_messages / total_messages * 100)
    data_bytes = data_messages['n_bytes'].sum()

    # Middleware messages analysis
    middleware_keywords = ['MIDDLEWARE']
    middleware_messages = df_analysis[
        df_analysis['messageType'].str.contains('|'.join(middleware_keywords), case=False, na=False)]
    total_middleware_messages = len(middleware_messages)
    middleware_percentage = (total_middleware_messages / total_messages * 100)
    middleware_bytes = middleware_messages['n_bytes'].sum()

    # Detailed subtype analysis for DATA_MESSAGES
    data_messages = df_analysis[df_analysis['messageType'].str.contains('DATA', case=False, na=False)]
    total_data_messages = len(data_messages)

    # Analyze subtypes within DATA_MESSAGES
    if not data_messages.empty:
        data_subtype_counts = data_messages['messageSubtype'].value_counts()
        data_subtype_percentages = (data_subtype_counts / total_data_messages * 100)

        # Bytes analysis by DATA_MESSAGE subtype
        data_subtype_bytes = data_messages.groupby('messageSubtype')['n_bytes'].agg(['sum', 'mean', 'count'])
        data_subtype_bytes['bytes_per_second'] = data_subtype_bytes['sum'] / duration_seconds
    else:
        data_subtype_counts = pd.Series()
        data_subtype_percentages = pd.Series()
        data_subtype_bytes = pd.DataFrame()

    # MONITORING_MESSAGE analysis
    monitoring_keywords = ['MONITORING_MESSAGE']
    monitoring_messages = df_analysis[
        df_analysis['messageType'].str.contains('|'.join(monitoring_keywords), case=False, na=False)]
    total_monitoring_messages = len(monitoring_messages)
    monitoring_percentage = (total_monitoring_messages / total_messages * 100)
    monitoring_bytes = monitoring_messages['n_bytes'].sum()

    # Lifecycle messages analysis - all messages that are not routing, data, middleware, or monitoring
    excluded_keywords = routing_keywords + data_keywords + middleware_keywords + monitoring_keywords
    lifecycle_messages = df_analysis[
        ~df_analysis['messageType'].str.contains('|'.join(excluded_keywords), case=False, na=False)
    ]
    total_lifecycle_messages = len(lifecycle_messages)
    lifecycle_percentage = (total_lifecycle_messages / total_messages * 100)
    lifecycle_bytes = lifecycle_messages['n_bytes'].sum()

    # Print comprehensive report with proper formatting
    print("=" * 60)
    print("MESSAGING METRICS ANALYSIS")
    print("=" * 60)

    print(f"\n BASIC METRICS:")
    print(f"• Total Messages: {total_messages:,}")
    print(f"• Total Bytes: {total_bytes:,} bytes")
    print(f"• Time Range: {start_time} to {end_time}")
    print(f"• Duration: {duration_seconds / 60:.2f} minutes")
    print(f"• Average Bytes/Second: {bytes_per_second_total:.2f} B/s")

    print(f"\n MESSAGE CATEGORIES ANALYSIS:")
    print(f"• Routing Messages: {total_routing_messages:,} Routing Bytes: {routing_bytes:,} bytes ({routing_percentage:.2f}%) Bytes/Second: "
          f"{routing_bytes / duration_seconds:.2f} B/s" if duration_seconds > 0 else "• Routing Bytes/Second: N/A")
    print(f"• Data Messages: {total_data_messages:,} ({data_percentage:.2f}%) Data Bytes: {data_bytes:,} bytes"
          f" Data Bytes/Second: {data_bytes / duration_seconds:.2f} B/s" if duration_seconds > 0 else "• Data Bytes/Second: N/A")
    print(f"• Middleware Messages: {total_middleware_messages:,} ({middleware_percentage:.2f}%) Middleware Bytes: {middleware_bytes:,} bytes "
          f"Middleware Bytes/Second: {middleware_bytes / duration_seconds:.2f} B/s" if duration_seconds > 0 else "• Midd Bytes/Second: N/A")
    print(f"• Lifecycle Messages: {total_lifecycle_messages:,} ({lifecycle_percentage:.2f}%) Lifecycle Bytes: {lifecycle_bytes:,} bytes "
        f"Lifecycle Bytes/Second: {lifecycle_bytes / duration_seconds:.2f} B/s" if duration_seconds > 0 else "• lifecycle Bytes/Second: N/A")
    print(f"• Monitoring Messages: {total_monitoring_messages:,} ({monitoring_percentage:.2f}%) Monitoring Bytes: {monitoring_bytes:,} bytes "
        f"Monitoring Bytes/Second: {monitoring_bytes / duration_seconds:.2f} B/s" if duration_seconds > 0 else "• lifecycle Bytes/Second: N/A")

    print(f"\n MESSAGE TYPE BREAKDOWN:")
    for msg_type, count in message_type_counts.items():
        percentage = message_type_percentages[msg_type]
        bytes_sum = bytes_by_message_type.loc[msg_type, 'sum'] if msg_type in bytes_by_message_type.index else 0
        avg_bytes = bytes_by_message_type.loc[msg_type, 'mean'] if msg_type in bytes_by_message_type.index else 0
        print(f"• {msg_type}: {count:,} messages ({percentage:.2f}%) - {bytes_sum:,} bytes ({avg_bytes:.1f} avg/msg)")

    print(f"\n MIDDLEWARE MESSAGE  DISTRIBUTION:")
    for strategy, count in strategy_counts.items():
        percentage = strategy_percentages[strategy]
        strategy_name = strategy if pd.notna(strategy) else 'None'
        print(f"• {strategy_name}: {count:,} messages ({percentage:.2f}%)")

    if not subtype_counts.empty:
        print(f"\n MESSAGE SUBTYPE ANALYSIS:")
        for subtype, count in subtype_counts.items():
            percentage = subtype_percentages[subtype]
            subtype_name = subtype if pd.notna(subtype) else 'None'
            print(f"• {subtype_name}: {count:,} messages ({percentage:.2f}%)")

    # DATA_MESSAGE SUBTYPE BREAKDOWN
    if not data_subtype_counts.empty:
        print(f"\nDATA_MESSAGE SUBTYPE BREAKDOWN:")
        print(f"Total DATA_MESSAGES: {total_data_messages:,}")
        for subtype, count in data_subtype_counts.items():
            percentage = data_subtype_percentages[subtype]
            subtype_data = data_subtype_bytes.loc[subtype] if subtype in data_subtype_bytes.index else None
            bytes_info = f" - {subtype_data['sum']:,} bytes ({subtype_data['mean']:.1f} avg, {subtype_data['bytes_per_second']:.2f} B/s)" if subtype_data is not None else ""
            print(f"  • {subtype}: {count:,} messages ({percentage:.2f}%){bytes_info}")

    print(f"\n BYTES ANALYSIS BY MESSAGE TYPE:")
    for msg_type in bytes_by_message_type.index:
        data = bytes_by_message_type.loc[msg_type]
        print(
            f"• {msg_type}: {data['sum']:,} total bytes, {data['mean']:.1f} avg bytes/msg, {data['bytes_per_second']:.2f} B/s")

    # Return structured results with raw numbers (no rounding)
    results = {
        'total_messages': total_messages,
        'total_bytes': total_bytes,
        'duration_seconds': duration_seconds,
        'bytes_per_second': bytes_per_second_total,
        'message_type_breakdown': message_type_counts.to_dict(),
        'message_type_percentages': {k: float(v) for k, v in message_type_percentages.items()},
        'strategy_breakdown': strategy_counts.to_dict(),
        'strategy_percentages': {k: float(v) for k, v in strategy_percentages.items()},
        'routing_messages': total_routing_messages,
        'data_messages': total_data_messages,
        'data_message_subtypes': data_subtype_counts.to_dict() if not data_subtype_counts.empty else {},
        'data_subtype_percentages': {k: float(v) for k, v in data_subtype_percentages.items()} if not data_subtype_percentages.empty else {},
        'data_subtype_bytes': data_subtype_bytes.to_dict() if not data_subtype_bytes.empty else {},
        'routing_percentage': float(routing_percentage),
        'data_percentage': float(data_percentage),
        'bytes_by_message_type': bytes_by_message_type.to_dict(),
        'time_range': {'start': start_time, 'end': end_time}
    }

    return results


def create_throughput_bar_plot(df, metrics, save_path: str, show_plot=False):
    """
    Create a standalone bar plot for throughput by message category
    """

    # Categorize messages into exactly four categories
    def categorize_message(row):
        message_type = str(row['messageType']).upper()

        if 'ROUTING' in message_type:
            return 'Routing Messages'  # Includes all routing (partial, full, other)
        elif 'MIDDLEWARE' in message_type:
            return 'Middleware Messages'
        elif 'DATA' in message_type:
            return 'Data Messages'
        else:
            # Everything else goes to Lifecycle (discovery, parent, lifecycle, heartbeat, etc.)
            return 'Lifecycle Messages'

    df_categorized = df.copy()
    df_categorized['category'] = df_categorized.apply(categorize_message, axis=1)

    # Calculate throughput (bytes per second) for each of the four categories
    category_throughput = df_categorized.groupby('category')['n_bytes'].sum() / metrics['duration_seconds']

    # Define the order of categories for consistent display
    category_order = ['Data Messages', 'Routing Messages', 'Middleware Messages', 'Lifecycle Messages']

    # Reorder the throughput data according to our desired order
    category_throughput = category_throughput.reindex(
        [cat for cat in category_order if cat in category_throughput.index])

    # Create bar plot
    fig = go.Figure()

    # Add bars for each category
    for i, category in enumerate(category_throughput.index):
        fig.add_trace(go.Bar(
            x=[category],
            y=[category_throughput[category]],
            name=category,
            marker_color=px.colors.qualitative.Plotly[i],
            text=[f'<b>{category_throughput[category]:.2f} B/s<b>'],
            textposition='outside',
            hovertemplate=f'<b>{category}</b><br>Throughput: {category_throughput[category]:.2f} B/s<extra></extra>'
        ))

    fig.update_layout(
        # title={
        #     'text': 'Throughput by Message Category',
        #     'x': 0.5,
        #     'xanchor': 'center',
        #     'font': dict(family='Helvetica', size=20, color='black')
        # },
        xaxis_title="Message Category",
        yaxis_title="Throughput (B/s)",
        showlegend=False,  # Since we're using colored bars with labels, legend isn't needed
        plot_bgcolor='white',
        font=dict(size=12),
        bargap=0.3  # Space between bars
    )

    # Customize axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        showgrid=False
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        gridcolor='lightgray'
    )
    if show_plot:
        fig.show()

    fig.write_image(save_path, scale=3)


def create_four_category_pie(df, save_path: str, show_plot=False):
    """
    Create a pie plot with exactly the four specified categories
    """

    def categorize_message_strict(message_type):
        message_type = str(message_type).upper()

        if 'MIDDLEWARE' in message_type:
            return 'Middleware'
        elif 'DATA' in message_type:
            return 'Data'
        elif 'ROUTING' in message_type:
            return 'Routing'
        else:
            return 'Lifecycle'  # Everything else goes to Lifecycle

    df_categorized = df.copy()
    df_categorized['category'] = df_categorized['messageType'].apply(categorize_message_strict)

    category_counts = df_categorized['category'].value_counts()

    # Option 1: Use Plotly's qualitative color sequences
    colors = px.colors.qualitative.Plotly[:4]  # First 4 colors from Plotly palette

    fig = go.Figure(data=[go.Pie(
        labels=category_counts.index,
        values=category_counts.values,
        hole=0.3,  # Donut chart style
        marker=dict(colors=colors),
        textinfo='percent+label',
        hovertemplate='<b>%{label} Messages</b><br>Percentage: %{percent}<br>Count: %{value}<extra></extra>'
    )])

    fig.update_layout(
        # title={
        #     'text': 'Message Distribution',
        #     'x': 0.5,
        #     'xanchor': 'center',
        #     'font': dict(family='Helvetica', size=20, color='black')
        # },
        showlegend=False,
    )

    # Customize axes
    fig.update_xaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        showgrid=False
    )

    fig.update_yaxes(
        title_font=dict(family='Helvetica', size=14),
        tickfont=dict(family='Helvetica', size=12),
        showgrid=False
    )
    if show_plot:
        fig.show()

    fig.write_image(save_path,
                    # width=1000,  # width in pixels
                    # height=600,  # height in pixels
                    scale=4)


# Get the default Plotly colors and extend with additional colors
plotly_colors = qualitative.Plotly

additional_colors = [
    qualitative.D3[5],
    qualitative.D3[2],
    qualitative.Dark24[23],
    qualitative.D3[7],
    qualitative.D3[8],
]

# Combine and remove duplicates while preserving order
extended_colors = list(dict.fromkeys(plotly_colors + additional_colors))


def summarize_inference_init_times(directory):
    times = []
    for file in [directory + "/" + f for f in os.listdir(directory) if f.startswith('run-app-init')]:
        with open(file, 'r') as f:
            data = json.load(f)
            for entry in data:
                if 'setup_time_ms' in entry:
                    times.append(entry['setup_time_ms'])
    if not times:
        print("No setup_time_ms values found.")
        return

    n = len(times)
    mean_time = sum(times) / n
    variance = sum((t - mean_time) ** 2 for t in times) / (n - 1 if n > 1 else 1)
    std_dev = math.sqrt(variance)

    # 95% confidence interval using normal approximation (z = 1.96)
    margin = 1.96 * std_dev / math.sqrt(n)
    ci_low = mean_time - margin
    ci_high = mean_time + margin

    print(f"======== Neural Network Initialization Stats ========")
    print(f"Samples: {n}")
    print(f"Mean setup time: {mean_time:.2f} ms")
    print(f"Std deviation: {std_dev:.2f} ms")
    print(f"Min setup time: {min(times)} ms")
    print(f"Max setup time: {max(times)} ms")
    print(f"95% CI: [{ci_low:.2f}, {ci_high:.2f}] ms")