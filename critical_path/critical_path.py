#!/usr/bin/env python

import typing
import networkx as nx
import matplotlib.pyplot as plt


def load_dot_as_digraph(path: str):
    """
    read_dot() returns a MultiDiGraph (multiple edges) but that isn't necessary for single weighted 
    edges, and causes problems when assigning weights.
    https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pydot.read_dot.html
    """
    print("Loading graph from dot file")
    G = nx.DiGraph(nx.nx_pydot.read_dot(path))
    G.remove_node("\\n")
    print(f"Graph loaded: {G}")
    return G


def read_edge_weights(path: str) -> typing.List[typing.List[any]]:
    from csv import reader
    with open(path, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Pass reader object to list() to get a list of lists
        list_of_rows = list(csv_reader)[1:]

        return list_of_rows


def get_edge_weight_for_node(node_weights: typing.List[typing.List[any]]) -> typing.Dict[any, any]:
    """
    Assigns a weight to edges based on a property of the predecessor node
    An example use case is to assign the task execution duration of a node to all edges where the node is the predecessor.
    """  
    result = dict([(u, int(w)) for u, w in node_weights])
    print(f"node_weights result: {result}")
    return result


# The predecessor node defines the weight for all edges between itself and any downstream successor nodes.
#  For example, if the duration of the node named `main` is 2 hours, the edges (main, parse), (main, cleanup), 
#  and all others like (main, *) have the same weight of 2.  
#  To do this, need the list of nodes with their execution duration.
#  There must always be a `end` task with no weight value.  
#  Every predecessor task must have at least one descendent, which will either be the `end` task or any other downstream task.
def get_edge_weights(G, node_weights: typing.List[typing.List[any]], default_weight: int = 1):
    """
    Convert a list of lists to a dict[n1]: weight
    """ 
    node_weight_map = get_edge_weight_for_node(node_weights)
    node_weights = {}
    for u, v in G.edges:
        node_weights[(u, v)] = node_weight_map.get(u, default_weight)
    print(f"node_weights: {node_weights}")
    return node_weights


def graph_filtered_by_nodes(graph, nodes: typing.List[any]):
    SG=G.subgraph( [n for n in G.nodes.keys() if n in nodes ] )
    print(f"{SG}")
    return SG


def draw_graph(G, filename: str, highlighted_edges=None, default_edge_color = 'blue', default_edge_highlight_color = 'red'):
    # Set the default color for all nodes
    for e in G.edges():
        G[e[0]][e[1]]['color'] = default_edge_color
    # Set highlighted edge colors, for critical path highlighting or other use cases
    if highlighted_edges:
        for u, v in highlighted_edges:
            G[u][v]['color'] = default_edge_highlight_color
    # Set all edge colors
    edge_color_list = [ G[e[0]][e[1]]['color'] for e in G.edges() ]
    nx.draw_planar(G, with_labels=True, edge_color=edge_color_list)
    plt.savefig(filename, format="PNG")
    plt.clf()


path = "sample_graph.dot"

G = load_dot_as_digraph(path=path)
print(f"\nNodes: {G.nodes}")
print(f"Edges: {G.edges}")

draw_graph(G, filename="Graph.png")

edge_weights_csv = read_edge_weights(path="edge_weights.csv")

edge_weights = get_edge_weights(G, edge_weights_csv)

nx.set_edge_attributes(G, edge_weights, "weight")
print("\n*** Weights assigned ***")
print(G)

longest_path_nodes = nx.dag_longest_path(G)
print(f"Longest path nodes: {longest_path_nodes}") 

SG = graph_filtered_by_nodes(graph=G, nodes = longest_path_nodes)

longest_path_nodes_filtered = nx.dag_longest_path(SG)
longest_path_length_filtered = nx.dag_longest_path_length(SG)

if longest_path_nodes_filtered != longest_path_nodes:
    raise Exception(
      "The filtered graph nodes must match the original longest path nodes because the filtered graph only contains the longest path"
      f"original nodes: {longest_path_nodes}, filtered nodes: {longest_path_nodes_filtered}"
      )

print(f"\nFiltered Nodes: {SG.nodes}") #debug
print(f"Filtered Edges: {SG.edges}") #debug
print(f"Filtered Weighted Edges: {nx.get_edge_attributes(SG, 'weight')}") #debug

draw_graph(SG, filename="SGraph.png")

draw_graph(G, filename="CriticalPathGraph.png", highlighted_edges=SG.edges)
