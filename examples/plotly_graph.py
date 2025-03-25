import networkx as nx
#import matplotlib.pyplot as plt
import plotly.graph_objects as go


def get_graph_figure():
    global G
    pos = nx.spring_layout(G)  # Layout for positioning nodes
    edge_x, edge_y = [], []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='gray')))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=10, color="lightblue"),
        text=node_text, textposition="top center"
    ))

    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


G = nx.DiGraph()
G.add_edge(1, 2)  # default edge data=1
G.add_edge(2, 3, weight=0.9)  # specify edge data

fig = get_graph_figure()
fig.show()
#nx.draw(G)
#plt.show()
