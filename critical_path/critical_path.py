#!/usr/bin/env python

import typing
import networkx as nx
import matplotlib.pyplot as plt
from uuid import uuid4
from csv import reader



# TODO: Change print statements to logging

class CriticalPath():
    """
    The predecessor node defines the weight for all edges between itself and any downstream successor nodes.
    For example, if the duration of the node named `main` is 2 hours, the edges (main, parse), (main, cleanup), 
    and all others like (main, *) have the same weight of 2.  
    To do this, need the list of nodes with their execution duration.
    There must always be a `end` task with no weight value.  
    Every predecessor task must have at least one descendent, which will either be the `end` task or any other downstream task.
    """
    EDGE_WEIGHT_KEY = "weight"

    def __init__(self, node_weights=None, graph=None):
        self.node_weights: typing.List[typing.List[any]] = node_weights
        self.graph: nx.DiGraph = graph
        self.critical_path_edges = None


    def set_graph(self, graph: nx.DiGraph):
        """
        Setter method
        """
        self.graph = graph


    def load_graph(self, path):
        """
        read_dot() returns a MultiDiGraph (multiple edges) but that isn't necessary for single weighted 
        edges, and causes problems when assigning weights.
        https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pydot.read_dot.html
        """
        print("\nLoading graph from dot file")
        G = nx.DiGraph(nx.nx_pydot.read_dot(path))
        G.remove_node("\\n")
        print(f"\tGraph loaded: {G}")
        print(f"\tNodes: {G.nodes}")
        print(f"\tEdges: {G.edges}")
        self.set_graph(graph=G)


    def set_weights(self, node_weights: typing.List[typing.List[any]]):
        """
        Setter method
        """
        self.node_weights = node_weights
 
 
    def load_weights(self, path):
        """
        Load weights from a csv file containing the node and the node property,
         to be assigned to all edge weights where that node is the predecessor
        """
        with open(path, 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Pass reader object to list() to get a list of lists
            node_weights = list(csv_reader)[1:]
            print(f"\nNode weight map from {path}: {node_weights}")
            self.set_weights(node_weights=node_weights)


    def run(self) -> typing.List[any]:
        """
        asdf
        """
        edge_weights = self._get_edge_weights()
        nx.set_edge_attributes(self.graph, edge_weights, self.EDGE_WEIGHT_KEY)
        longest_path_nodes = nx.dag_longest_path(self.graph)
        self.critical_path_edges = self._get_edges_from_ordered_list_of_nodes(longest_path_nodes)


    def save_image(self, path: str = None):
        """
        asdf
        """
        default_edge_color='blue'
        default_edge_highlight_color ='red'
        save_path= path or "../target"
        filename="CriticalPathGraph"

        print("\nDrawing graph")
        # Set the default color for all nodes
        for u, v in self.graph.edges():
            self.graph[u][v]['color'] = default_edge_color
        # Set highlighted edge colors, for critical path highlighting or other use cases
        for u, v in self.critical_path_edges:
            self.graph[u][v]['color'] = default_edge_highlight_color
        # Set all edge colors
        edge_color_list = [ self.graph[u][v]['color'] for u, v in self.graph.edges() ]
        pos=nx.planar_layout(self.graph)
        edge_labels = nx.get_edge_attributes(self.graph, self.EDGE_WEIGHT_KEY)

        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)
        nx.draw_planar(self.graph, with_labels=True, edge_color=edge_color_list)
        filename_full = f"{save_path}/{filename}-{uuid4()}.png"
        print(f"\tSaving image to: {filename_full} ")
        plt.savefig(filename_full, format="PNG")
        print("\tDone saving image")
        plt.clf()


    def _get_edge_weights(self, default_weight: int = 1):
        """
        Assign the same weight to all edges of u.  
        Needed for critical path calcs.
        """
        node_weight_map = dict([(u, int(w)) for u, w in self.node_weights])
        print(f"\nEdge weights for node: {node_weight_map}")
        result = {(u, v): node_weight_map.get(u, default_weight) for u, v in self.graph.edges }
        print(f"\nEdge weights: {result}")
        return result


    @staticmethod
    def _get_edges_from_ordered_list_of_nodes(nodes: typing.List[any]):
        """
        For each ordered pair of nodes in the list, 
        create a list of tuples in the same order 
        """
        edges = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
        print(f"\nEdges from ordered list of nodes: {edges}") 

        return edges


if __name__ == "__main__":

    def run():
        print("\n*** Calculating the critical path ***")
        
        print("\nParsing command line options.")
        import optparse
        p = optparse.OptionParser()
        p.add_option('--graph', '-g', default="input/sample_graph.dot")
        p.add_option('--weights', '-w', default="input/sample_weights.csv")
        p.add_option('--image-target', '-i', default="../target")
        options, arguments = p.parse_args()

        print(f"\tOptions parsed: {options}")
        print(f"\tArguments parsed: {arguments}")
        cp = CriticalPath()
        cp.load_graph(path=options.graph)
        cp.load_weights(path=options.weights)
        cp.run()
        cp.save_image()
    
    run()
