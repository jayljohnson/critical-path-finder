#!/usr/bin/env python

import typing
import logging
import networkx as nx
import matplotlib.pyplot as plt  # type: ignore
from uuid import uuid4
from csv import reader
import click
import json

from exceptions import NodeWeightsDuplicateValues, MissingInputsException, RunBeforeSaveException

logging.basicConfig(
    encoding='utf-8',
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class CriticalPath():
    """
    Implements task-on-node approach to Critical Path Management (CPM).  Returns the longest path based on the node duration, cost, or other quantifiable attribute.
    * To implement task-on-node, the edge weight is the same value for all edges of which the task is the predecessor node.
    * For example, if the duration of the node (task) named `main` is 2 hours, the edges (main, parse), (main, cleanup),
    and all others like (main, *) have the same weight of 2.  
    
    The variables `u`, `v` represent the predecessor (parent) and successor (child) nodes of an edge.  This naming convention is borrowed from the networkx package.
    """
    EDGE_WEIGHT_ATTRIBUTE_NAME = "weight"
    EDGE_COLOR_ATTRIBUTE_NAME = "color"

    def __init__(self, graph: nx.DiGraph=None, node_weights_map:typing.Dict[any, int]=None):
        logging.info("Creating CriticalPath object")
        # The weight values are ints to simplify the calculations and validation.
        # Take care that the inputs and outputs are treated as the same units,
        # for example as hours, minutes or seconds.  Unit conversion and fractional units are not supported within the module.
        # Inputs
        self.graph = graph
        self.node_weights_map = node_weights_map
        # Output
        self.critical_path_edges = None
        # Used mostly for validation; persisted for quick access to the sum of the critical path edge weights
        self.critical_path_length = None

    @property
    def edge_weights(self) -> typing.Dict[tuple, int]:
        """
        Assign the same weight to all edges of u.

        The graph assumes task-on-node.
        Therefore all edges that have the same predecessor node `u` also share the same weight.
        """
        self.validate()
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


    def load_graph_from_dot_file(self, path):
        """
        Reads a graphviz .dot file representing a digraph.
        """
        logging.info("Loading graph from dot file")
        G = nx.DiGraph(nx.nx_pydot.read_dot(path))
        # Cleanup newlines in the .dot file that get loaded as nodes
        G.remove_node("\\n")
    
        logging.debug(
            f"\tGraph loaded: {G}"
            f"\tNodes: {G.nodes}"
            f"\tEdges: {G.edges}"
            )
        self.graph = G


    def load_weights(self, path) -> None:
        """
        Load weights from a csv file containing the node and the node weight.  
        The node weight is later assigned to all edge weights where the node is the predecessor.
        """
        with open(path, 'r') as read_obj:
            csv_reader = reader(read_obj)
            node_weights = list(csv_reader)[1:]
            node_weights_map = {}
            for i, (node, weight) in enumerate(node_weights):
                if not node_weights_map.get(node):
                    node_weights_map[node] = int(weight)
                else:
                    raise NodeWeightsDuplicateValues(
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
            raise MissingInputsException("Undefined instance variable: self.node_weights_map")

        if not self.graph:
            raise MissingInputsException("Undefined instance variable: self.graph")

    def find(self) -> typing.Dict[tuple, int]:
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

        logging.info(
            f"Critical path result: {result}"
            f"Critical path length: {self.critical_path_length}"
            )
        
        # Validate that the sum of edge weights matches the value of self.critical_path_length
        edge_weights_sum = sum(result.values())
        if edge_weights_sum != self.critical_path_length:
            raise Exception(
                f"The sum of edge weights `{edge_weights_sum}` must be the same as the self.critical_path_length `{self.critical_path_length}`"
            )

        return result

    def save_image(self, path: str) -> None:
        """
        Generate an image of the graph with the critical path highlighted in a different color than other edges
        """
        EDGE_COLOR_DEFAULT = "blue"
        EDGE_COLOR_CRITICAL_PATH = "red"
        FILE_EXTENSION = "png"
        FILENAME_PREFIX = "CriticalPathGraph"

        self.validate()
        if not self.critical_path_edges:
            raise RunBeforeSaveException(
                "Undefined instance variable: self.critical_path_edges."
                "Must call self.find() to calculate the critical path, "
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
    
    @staticmethod
    def _get_digraph_from_tuples(graph: typing.List[tuple]):
        """
        Reads a list of tuples representing a digraph.
        """
        logging.info("Loading graph from list of tuples")
        G = nx.DiGraph(graph)
        logging.debug(
            f"\tGraph loaded: {G}"
            f"\tNodes: {G.nodes}"
            "\tEdges: {G.edges}"
            )
        return G


if __name__ == "__main__":

    @click.command()
    @click.option('-g', '--graph', default="input/sample_graph.dot", help="File location for DiGraph .dot file")
    @click.option('-w', '--weights', default="input/sample_weights.csv", help="File location for edge weights")
    @click.option('-i', '--image-target', help="File location to write the graph as a .png file")
    def main(graph, weights, image_target):
        """
        Used by the CLI.
        Calculate the critical path and save an image of the graph.
        Requires the graph and weights to be stored as a file before running.
        """
        logging.info("*** Calculating the critical path ***")
        cp = CriticalPath()
        cp.load_graph_from_dot_file(path=graph)
        cp.load_weights(path=weights)
        critical_path = cp.find()
        if image_target:
            cp.save_image(path=image_target)
        else:
            logging.debug("Skipping image creation.  To save an image, run with the -i flag set to the image target directory.")
        import sys
        sys.stdout.write(str(critical_path))
        sys.exit(0)

    main()
