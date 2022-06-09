#!/usr/bin/env python

import typing
import networkx as nx
import matplotlib.pyplot as plt
from uuid import uuid4

# The predecessor node defines the weight for all edges between itself and any downstream successor nodes.
#  For example, if the duration of the node named `main` is 2 hours, the edges (main, parse), (main, cleanup), 
#  and all others like (main, *) have the same weight of 2.  
#  To do this, need the list of nodes with their execution duration.
#  There must always be a `end` task with no weight value.  
#  Every predecessor task must have at least one descendent, which will either be the `end` task or any other downstream task.
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
    print(f"\nNodes: {G.nodes}")
    print(f"\nEdges: {G.edges}")
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
    print(f"Edge weights for node: {result}")
    return result


def get_edge_weights(G, node_weights: typing.List[typing.List[any]], default_weight: int = 1):
    """
    Assign the same weight to all edges of u.  Needed for critical path calcs.
    """ 
    node_weight_map = get_edge_weight_for_node(node_weights)
    result = {(u, v): node_weight_map.get(u, default_weight) for u, v in G.edges }
    print(f"Edge weights: {result}")
    return result


def get_edges_from_ordered_list_of_nodes(nodes: typing.List[any]):
    edges = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
    print(f"Longest path edges: {edges}") 

    return edges


def draw_graph(
        G, filename: str, 
        highlighted_edges=None, 
        default_edge_color = 'blue', 
        default_edge_highlight_color = 'red',
        edge_labels = None):
    # Set the default color for all nodes
    for u, v in G.edges():
        G[u][v]['color'] = default_edge_color
    # Set highlighted edge colors, for critical path highlighting or other use cases
    if highlighted_edges:
        for u, v in highlighted_edges:
            G[u][v]['color'] = default_edge_highlight_color
    # Set all edge colors
    edge_color_list = [ G[u][v]['color'] for u, v in G.edges() ]
    pos=nx.planar_layout(G)
    nx.draw_networkx_edge_labels(G,pos=pos,edge_labels=edge_labels)
    nx.draw_planar(G, with_labels=True, edge_color=edge_color_list)
    plt.savefig(f"../target/{filename}-{uuid4()}.png", format="PNG")
    plt.clf()


path = "input/sample_graph.dot"

G = load_dot_as_digraph(path=path)

edge_weights_csv = read_edge_weights(path="input/edge_weights.csv")

edge_weights = get_edge_weights(G, edge_weights_csv)

nx.set_edge_attributes(G, edge_weights, "weight")

longest_path_nodes = nx.dag_longest_path(G)
longest_path_edges = get_edges_from_ordered_list_of_nodes(longest_path_nodes)

labels = nx.get_edge_attributes(G,'weight')

draw_graph(
    G, 
    filename="CriticalPathGraph", 
    highlighted_edges=longest_path_edges,
    edge_labels=labels
    )
