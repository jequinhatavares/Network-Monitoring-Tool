import os


from app_common import *


def plot_scatter_message_continuous2(df: pd.DataFrame,show_plot):
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
        "TOP_PARENT_LIST_ADVERTISEMENT_REQUEST": "Parent List Advertisement Request",
        "TOP_PARENT_LIST_ADVERTISEMENT": "Parent List Advertisement",
        "TOP_PARENT_ASSIGNMENT_COMMAND": "Parent Assignment Command",
        "TOP_METRICS_REPORT": "Metrics Report",
        "TOP_NODE_UPDATE": "Node Update",
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

        "Parent List Advertisement",
        "Metrics Report",
        "Node Update",
    ]


    # Gather the data that is going to be displayed with the types or subtypes
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
                     color_discrete_sequence=extended_colors,
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
    if(show_plot):
        fig.show()

    fig.write_image("images/nn_topology/messages_d_nn_12_topology.png",
                    width=1000,
                    height=600,
                    scale=4)



if __name__ == '__main__':
    show_plots = False

    app_init_df, app_inference_df, message_continuous_df = get_dfs("logs/distributed_nn_12_strategy_topology", 2)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None,
    #                        'display.max_colwidth', None):
    #     print(app_init_df)
    #     print(app_inference_df)
    #     print(message_continuous_df)

    clean_df(message_continuous_df)

    results = analyze_message_metrics(message_continuous_df)

    plot_scatter_message_continuous2(message_continuous_df,show_plots)

    plot_scatter_inference_time(app_inference_df, "images/nn_topology/inference_time_d_nn_12_topology.png", show_plots)

    create_throughput_bar_plot(message_continuous_df, results, "images/nn_topology/throughput_d_nn_12_topology.png", show_plots)

    create_four_category_pie(message_continuous_df, "images/nn_topology/messages_pie_d_nn_12_topology.png", show_plots)

