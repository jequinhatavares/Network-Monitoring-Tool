import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
G.add_edge(1, 2)  # default edge data=1
G.add_edge(2, 3, weight=0.9)  # specify edge data
#G = nx.cubical_graph()

nx.draw(G)
plt.show()
