#!/usr/bin/env python

import typing
import logging
import networkx as nx
import matplotlib.pyplot as plt  # type: ignore
from uuid import uuid4
from csv import reader
import optparse


logging.basicConfig(
    filename='../target/logs/critical-path.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class CriticalPath():
    """
    Task-on-node approach to CPM.  
    Throughout this module, the variables `u`, `v` denote the predecessor and successor nodes of an edge.
    The edge weight is the same value for all edges of which the task is the predecessor node.
    For example, if the duration of the node (task) named `main` is 2 hours, the edges (main, parse), (main, cleanup),
    and all others like (main, *) have the same weight of 2.
    """
    EDGE_WEIGHT_ATTRIBUTE_NAME = "weight"
    EDGE_COLOR_ATTRIBUTE_NAME = "color"

    # None is the default intentionally to support loading from files from the CLI.
    # If importing this into another python application, directly pass in the objects
    def __init__(self, node_weights_map=None, graph=None):
        logging.info("Creating CriticalPath object")
        # The weight values are ints to simplify the calculations and validation.
        # Be sure that the inputs and outputs are treated as the same units,
        # for example as minutes or seconds depending on how granular of a result is needed
        self.graph: nx.DiGraph = graph
        self.node_weights_map: typing.Dict[any, int] = node_weights_map
        self.critical_path_edges = None
        self.critical_path_length = None

    @property
    def edge_weights(self) -> typing.Dict[tuple, int]:
        """
        Assign the same weight to all edges of u.

        The graph assumes task-on-node.
        Therefore all edges that have the same predecessor node `u` also share the same weight.
        """
        for node in self.node_weights_map.keys():
            if node not in self.graph.nodes:
                raise Exception(
                    f"Node {node} from self.node_weights_map does not exist in self.graph.nodes"
                )
        try:
            result = {(u, v): self.node_weights_map[u] for u, v in self.graph.edges}
        except KeyError as e:
            raise KeyError(f"The graph node {e} does not exist in self.node_weights_map")
        logging.debug(f"Edge weights: {result}")
        return result

    def load_graph(self, path):
        """
        Reads a dotviz .dot file representing a digraph.
        Used by CLI -g flag to pass in a file path.
        """
        logging.info("Loading graph from dot file")
        G = nx.DiGraph(nx.nx_pydot.read_dot(path))
        G.remove_node("\\n")
        logging.debug(f"\tGraph loaded: {G}")
        logging.debug(f"\tNodes: {G.nodes}")
        logging.debug(f"\tEdges: {G.edges}")
        self.graph = G

    def load_weights(self, path) -> None:
        """
        Load weights from a csv file containing the node and the node property,
         to be assigned to all edge weights where that node is the predecessor
        Used by CLI -w flag to pass in a file path.
        """
        with open(path, 'r') as read_obj:
            csv_reader = reader(read_obj)
            node_weights = list(csv_reader)[1:]
            node_weights_map = {}
            for i, (node, weight) in enumerate(node_weights):
                if not node_weights_map.get(node):
                    node_weights_map[node] = int(weight)
                else:
                    raise Exception(
                        "The node weights csv file requires unique node values in column 1.  "
                        f"Node value `{node}` is duplicated on row {i+1}: {node_weights[i]}"
                    )
            logging.debug(f"Node weight map from {path}: {node_weights_map}")
            self.node_weights_map = node_weights_map

    def validate(self) -> None:
        """
        Validate that required instance variables exist before running calcs
        """
        if not self.node_weights_map:
            raise Exception("Undefined instance variable: self.node_weights_map")

        if not self.graph:
            raise Exception("Undefined instance variable: self.graph")

    def run(self) -> typing.Dict[tuple, int]:
        """
        Calculate the critical path and return the list of critical path edges
        """
        self.validate()
        edge_weights = self.edge_weights
        nx.set_edge_attributes(self.graph, edge_weights, self.EDGE_WEIGHT_ATTRIBUTE_NAME)

        longest_path_nodes = nx.dag_longest_path(self.graph)
        self.critical_path_edges = self._get_edges_from_ordered_list_of_nodes(longest_path_nodes)
        self.critical_path_length = nx.dag_longest_path_length(self.graph)
        result = {(u, v): edge_weights[(u, v)] for u, v in self.critical_path_edges}

        logging.info(f"Critical path result: {result}")
        logging.info(f"Critical path length: {self.critical_path_length}")
        
        # Validate that the sum of edge weights matches the value of self.critical_path_length
        edge_weights_sum = sum(result.values())
        if edge_weights_sum != self.critical_path_length:
            raise Exception(
                f"The sum of edge weights `{edge_weights_sum}` must be the same as the self.critical_path_length `{self.critical_path_length}`"
            )

        return result

    def save_image(self, path: str) -> None:
        """
        Generate an image of the graph with the critical path highlighted
        """
        EDGE_COLOR_DEFAULT = "blue"
        EDGE_COLOR_CRITICAL_PATH = "red"
        FILE_EXTENSION = "png"
        FILENAME_PREFIX = "CriticalPathGraph"

        self.validate()
        if not self.critical_path_edges:
            raise Exception(
                "Undefined instance variable: self.critical_path_edges."
                "Must call self.run() to calculate the critical path, "
                "before calling self.save_image()."
            )

        logging.info("Drawing graph")
        # Assign edge labels
        edge_labels = nx.get_edge_attributes(self.graph, self.EDGE_WEIGHT_ATTRIBUTE_NAME)
        pos = nx.planar_layout(self.graph)
        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)

        # Set a default color so that attribute keys exist for all edges
        for u, v in self.graph.edges():
            self.graph[u][v][self.EDGE_COLOR_ATTRIBUTE_NAME] = EDGE_COLOR_DEFAULT
        # Update the edge color highlighting the critical path edges
        for u, v in self.critical_path_edges:
            self.graph[u][v][self.EDGE_COLOR_ATTRIBUTE_NAME] = EDGE_COLOR_CRITICAL_PATH
        # Fetch all edge colors and assign to the graph drawing
        edge_color_list = [self.graph[u][v][self.EDGE_COLOR_ATTRIBUTE_NAME] for u, v in self.graph.edges()]
        logging.debug(f"\tEdge color list: {edge_color_list} ")
        nx.draw_planar(self.graph, with_labels=True, edge_color=edge_color_list)

        filename_full = f"{path}/{FILENAME_PREFIX}-{uuid4()}.{FILE_EXTENSION}"
        logging.info(f"\tSaving image to: {filename_full} ")
        plt.savefig(filename_full, format=FILE_EXTENSION)
        logging.debug("\tDone saving image")
        plt.clf()

    @staticmethod
    def _get_edges_from_ordered_list_of_nodes(nodes: typing.List[any]) -> typing.List[tuple]:
        """
        Convert ordered list of individual nodes to an ordered list of edge tuples.
        The successor node of one tuple becomes the predecessor node of the next tuple.
        """
        result = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
        logging.debug(f"Edges from ordered list of nodes: {result}")

        return result


if __name__ == "__main__":

    def main():
        """
        Used by the CLI.
        Calculate the critical path and save an image of the graph.
        Requires the graph and weights to be stored as a file before running.
        """
        logging.info("*** Calculating the critical path ***")
        logging.debug("Parsing command line options.")
        p = optparse.OptionParser()
        p.add_option('--graph', '-g', default="input/sample_graph.dot")
        p.add_option('--weights', '-w', default="input/sample_weights.csv")
        p.add_option('--image-target', '-i')  # If this flag is omitted, no image file is saved
        options, arguments = p.parse_args()

        logging.debug(f"\tOptions parsed: {options}")
        logging.debug(f"\tArguments parsed: {arguments}")
        cp = CriticalPath()
        cp.load_graph(path=options.graph)
        cp.load_weights(path=options.weights)
        critical_path = cp.run()
        if options.image_target:
            cp.save_image(path=options.image_target)
        else:
            logging.debug("Skipping image creation.  To save an image, run with the -i flag set to the image target directory.")
        import sys
        sys.stdout.write(str(critical_path))
        sys.exit(0)

    main()
