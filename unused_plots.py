import pandas as pd


def box_plot_with_3_devices_by_state(df: pd.DataFrame):
    states = ['init_time', 'search_time', 'join_time']
    state_labels = {
        'init_time': 'Init State',
        'search_time': 'Search State',
        'join_time': 'Join State'
    }
    devices = ['ESP8266', 'ESP32', 'RPI']

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[state_labels[state] for state in states],
        horizontal_spacing=0.08  # Slightly more spacing
    )

    for i, state in enumerate(states, start=1):
        for j, device in enumerate(devices):
            sub_df = df[df["type"] == device]
            time_seconds = sub_df[state] / 1000  # Convert to seconds

            fig.add_trace(go.Box(
                y=time_seconds,
                name=device,
                marker_color=device_colors[device],
                line=dict(width=2),  # Thicker box lines
                # boxpoints=False,  # no individual data points
                width=0.5,  # Slightly wider boxes
                offsetgroup=j,
                showlegend=(i == 1)
            ), row=1, col=i)

    # Font settings
    font_settings = dict(family='Helvetica')
    title_font = dict(family='Helvetica', size=20)
    axis_title_font = dict(family='Helvetica', size=14)
    tick_font = dict(family='Helvetica', size=12)

    # Update layout
    fig.update_layout(
        title={
            'text': 'Device Performance by State',
            'x': 0.5,
            'xanchor': 'center',
            'font': title_font
        },
        font=font_settings,
        boxmode='group',
        legend={'font': tick_font},
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=60, r=60)
    )

    # Update all y-axes
    for i in range(1, 4):
        fig.update_yaxes(
            title_text='Time (s)',
            title_font=axis_title_font,
            tickfont=tick_font,
            row=1, col=i
        )
        fig.update_xaxes(
            title_text='',
            tickfont=tick_font,
            row=1, col=i
        )

    # Update subplot titles
    for i in range(3):
        fig.layout.annotations[i].update(font=dict(family='Helvetica', size=16, color='black'))

    fig.show()




def bar_plot_with_3_devices_by_state(df: pd.DataFrame):
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

    # Add traces for each state (stacked)
    for i, state in enumerate(states):
        state_means = [result[state] for result in results]
        state_percentages = [result[f'{state}_pct'] for result in results]

        # Create hover text with both time and percentage
        hover_text = []
        for j, device in enumerate(devices):
            time_val = state_means[j]
            pct_val = state_percentages[j]
            hover_text.append(
                f"{state_labels[state]}<br>" +
                f"Time: {time_val:.3f}s<br>" +
                f"Percentage: {pct_val:.1f}%"
            )

        fig.add_trace(go.Bar(
            x=devices,
            y=state_means,
            name=state_labels[state],
            marker_color=state_colors,
            text=[f'{pct:.1f}%' for pct in state_percentages],
            textposition='inside',
            textfont=dict(color='white', weight='bold', size=11),
            hovertemplate=hover_text,
            hoverinfo='text'
        ))

    # Update layout
    title_font = dict(family='Helvetica', size=18, color='black')
    axis_title_font = dict(family='Helvetica', size=15, color='black')
    tick_font = dict(family='Helvetica', size=12, color='black')
    legend_font = dict(family='Helvetica', size=12, color='black')

    fig.update_layout(
        title={
            'text': 'Device Integration Time Breakdown',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': title_font
        },
        xaxis_title='Device',
        yaxis_title='Time (seconds)',
        barmode='stack',
        font=dict(family='Helvetica', size=12),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100, b=60, l=60, r=60),
        legend={
            'font': legend_font,
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'center',
            'x': 0.5
        },
        hovermode='x unified'
    )

    # Customize axes
    fig.update_xaxes(
        title_font=axis_title_font,
        tickfont=tick_font
    )

    fig.update_yaxes(
        title_font=axis_title_font,
        tickfont=tick_font,
        gridcolor='lightgray',
        gridwidth=0.5
    )

    # Add total time annotations on top of each bar
    for i, device in enumerate(devices):
        total_time = results[i]['total_time']
        fig.add_annotation(
            x=device,
            y=total_time,
            text=f'Total: {total_time:.2f}s',
            showarrow=False,
            yshift=25,
            font=dict(family='Helvetica', size=13, weight='bold', color='black'),
            bgcolor='white',
            bordercolor='gray',
            borderwidth=1,
            borderpad=4,
            opacity=0.9
        )

    fig.show()



def plot_scatter_message_continuous_with_annotations(df: pd.DataFrame):
    # Convert timestamp to relative seconds (starting from 0)
    first_timestamp = df['timestamp'].iloc[0]
    df['relative_time'] = df['timestamp'] - first_timestamp

    # Create human-readable message type labels and acronyms

    message_type_mapping = {
        'PARENT_DISCOVERY_REQUEST': 'Parent Discovery Request',
        'CHILD_REGISTRATION_REQUEST': 'Child Registration Request',
        'MONITORING_MESSAGE': 'Monitoring Message',
        'PARTIAL_ROUTING_TABLE_UPDATE': 'Partial Routing Update',
        'FULL_ROUTING_TABLE_UPDATE': 'Full Routing Update',
    }
    message_type_acronyms = {
        'Parent Discovery Request': 'PDR',
        'Child Registration Request': 'CRR',
        'Monitoring Message': 'MonM',
        'Partial Routing Update': 'PRU',
        'Full Routing Update': 'FRU'
    }

    df['messageType_readable'] = df['messageType'].map(message_type_mapping)

    # Calculate statistics for annotations
    total_messages = len(df)
    total_bytes = df['n_bytes'].sum()
    time_span = df['relative_time'].max()
    msg_frequency = total_messages / time_span if time_span > 0 else 0
    avg_bytes_per_second = total_bytes / time_span if time_span > 0 else 0
    avg_msg_size = df['n_bytes'].mean()

    # Calculate message type statistics
    msg_type_stats = df.groupby('messageType_readable').agg({
        'n_bytes': ['count', 'mean', 'sum']
    }).round(2)
    msg_type_stats.columns = ['count', 'avg_size', 'total_bytes']

    # Create the scatter plot
    fig = px.scatter(df,
                     x='relative_time',
                     y='n_bytes',
                     color='messageType_readable',
                     title='',
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
        height=600,
        margin=dict(r=200)  # Increase right margin to accommodate annotations
    )

    # Customize the markers - make them larger and more visible
    fig.update_traces(
        marker=dict(
            size=12,  # Larger balls where
            opacity=0.8,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )

    # Customize axes
    fig.update_xaxes(
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    fig.update_yaxes(
        gridcolor='lightgray',
        griddash='dash',
        showgrid=True
    )

    # Create analysis summary text
    summary_text = [
        "<b>Analysis Summary</b>",
        f"Total Messages: {total_messages}",
        f"Total Bytes: {total_bytes:,}",
        f"Time Span: {time_span:.2f}s",
        f"Avg Throughput: {avg_bytes_per_second:.2f} bytes/s",
    ]

    # Create message statistics text with acronyms
    stats_text = ["<b>Message Statistics</b>"]
    for msg_type in df['messageType_readable'].unique():
        stats = msg_type_stats.loc[msg_type]
        percentage = (stats['count'] / total_messages) * 100
        acronym = message_type_acronyms.get(msg_type, msg_type[:3].upper())
        stats_text.append(f"{acronym}:")
        stats_text.append(f"  {stats['count']} messages ({percentage:.1f}%)")
        stats_text.append(f"  Avg: {stats['avg_size']} bytes")

    # Add annotations above the legend (message types caption)
    fig.add_annotation(
        x=1.277,  # Position to the right of the legend
        y=0.59,  # Above the legend
        xref="paper",
        yref="paper",
        text="<br>".join(summary_text),
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        borderpad=4,
        align="left",
        font=dict(size=10)
    )

    fig.add_annotation(
        x=1.26,  # Position to the right of the legend
        y=0.0,  # Below the summary
        xref="paper",
        yref="paper",
        text="<br>".join(stats_text),
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        borderpad=4,
        align="left",
        font=dict(size=10)
    )

    # Show the plot
    fig.show()


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

