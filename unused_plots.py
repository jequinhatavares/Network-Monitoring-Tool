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