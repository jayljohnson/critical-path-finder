#!/usr/bin/env python

import typing
import logging
import networkx as nx
import matplotlib.pyplot as plt
from uuid import uuid4
from csv import reader


logging.basicConfig(filename='../target/example.log', encoding='utf-8', level=logging.INFO)

class CriticalPath():
    """
    The predecessor node defines the weight for all edges between itself and any downstream successor nodes.
    For example, if the duration of the node named `main` is 2 hours, the edges (main, parse), (main, cleanup), 
    and all others like (main, *) have the same weight of 2.
    To do this, need the list of nodes with their execution duration.
    There must always be a `end` task with no weight value.
    Every predecessor task must have at least one descendent, which will either be the `end` task or any other downstream task.
    """
    EDGE_WEIGHT_ATTRIBUTE_NAME = "weight"

    # None is the default intentionally to support loading from files from the CLI.
    # If importing this into another python application, directly pass in the objects
    def __init__(self, node_weights=None, graph=None):
        self.node_weights: typing.List[typing.List[any]] = node_weights
        self.graph: nx.DiGraph = graph
        # This gets set after calling the run() method; it's also the CLI output
        self.critical_path_edges = None


    def load_graph(self, path):
        """
        Reads a dotviz .dot file representing a digraph.  
        Used by CLI -g flag to pass in a file path.
        """
        logging.info("\nLoading graph from dot file")
        G = nx.DiGraph(nx.nx_pydot.read_dot(path))
        G.remove_node("\\n")
        logging.info(f"\tGraph loaded: {G}")
        logging.info(f"\tNodes: {G.nodes}")
        logging.info(f"\tEdges: {G.edges}")
        self.graph=G


    def load_weights(self, path):
        """
        Load weights from a csv file containing the node and the node property,
         to be assigned to all edge weights where that node is the predecessor
        Used by CLI -w flag to pass in a file path.
        """
        with open(path, 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Pass reader object to list() to get a list of lists
            node_weights = list(csv_reader)[1:]
            logging.info(f"\nNode weight map from {path}: {node_weights}")
            self.node_weights=node_weights


    def run(self) -> typing.List[any]:
        """
        Calculate the critical path and return the list of critical path edges
        """
        edge_weights = self._get_edge_weights()
        nx.set_edge_attributes(self.graph, edge_weights, self.EDGE_WEIGHT_ATTRIBUTE_NAME)
        longest_path_nodes = nx.dag_longest_path(self.graph)
        self.critical_path_edges = self._get_edges_from_ordered_list_of_nodes(longest_path_nodes)
        return self.critical_path_edges


    def save_image(self, path: str):
        """
        Generate an image of the graph with the critical path highlighted
        """
        EDGE_COLOR_DEFAULT = 'blue'
        EDGE_COLOR_CRITICAL_PATH ='red'
        SAVE_PATH = path
        FILENAME_PREFIX = "CriticalPathGraph"

        logging.info("\nDrawing graph")
        # Set the default color for all nodes
        for u, v in self.graph.edges():
            self.graph[u][v]['color'] = EDGE_COLOR_DEFAULT
        # Set highlighted edge colors, for critical path highlighting or other use cases
        for u, v in self.critical_path_edges:
            self.graph[u][v]['color'] = EDGE_COLOR_CRITICAL_PATH
        # Set all edge colors
        edge_color_list = [ self.graph[u][v]['color'] for u, v in self.graph.edges() ]
        pos=nx.planar_layout(self.graph)
        edge_labels = nx.get_edge_attributes(self.graph, self.EDGE_WEIGHT_ATTRIBUTE_NAME)

        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)
        nx.draw_planar(self.graph, with_labels=True, edge_color=edge_color_list)
        filename_full = f"{SAVE_PATH}/{FILENAME_PREFIX}-{uuid4()}.png"
        logging.info(f"\tSaving image to: {filename_full} ")
        plt.savefig(filename_full, format="PNG")
        logging.info("\tDone saving image")
        plt.clf()


    def _get_edge_weights(self, default_weight: int = 1):
        """
        Assign the same weight to all edges of u.  
        Needed for critical path calcs.
        """
        node_weight_map = dict([(u, int(w)) for u, w in self.node_weights])
        logging.info(f"\nEdge weights for node: {node_weight_map}")
        result = {(u, v): node_weight_map.get(u, default_weight) for u, v in self.graph.edges }
        logging.info(f"\nEdge weights: {result}")
        return result


    @staticmethod
    def _get_edges_from_ordered_list_of_nodes(nodes: typing.List[any]):
        """
        For each ordered pair of nodes in the list, 
        create a list of tuples in the same order 
        """
        edges = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
        logging.info(f"\nEdges from ordered list of nodes: {edges}") 

        return edges


if __name__ == "__main__":

    def run():
        """
        Calculate the critical path and save an image of the graph
        Also does handling of cli arguments
        """
        logging.info("\n*** Calculating the critical path ***")
        logging.info("\nParsing command line options.")
        import optparse
        p = optparse.OptionParser()
        p.add_option('--graph', '-g', default="input/sample_graph.dot")
        p.add_option('--weights', '-w', default="input/sample_weights.csv")
        p.add_option('--image-target', '-i')
        options, arguments = p.parse_args()

        logging.info(f"\tOptions parsed: {options}")
        logging.info(f"\tArguments parsed: {arguments}")
        cp = CriticalPath()
        cp.load_graph(path=options.graph)
        cp.load_weights(path=options.weights)
        critical_path = cp.run()
        if options.image_target: # , default="../target"
            cp.save_image(path=options.image_target)
        else:
            logging.info("Skipping image creation")
        import sys
        sys.stdout.write(str(critical_path))
        sys.exit(0)
    
    run()
