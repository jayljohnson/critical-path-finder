# Quick Start

1. Run from the CLI by:
   1. Using the provided sample inputs with `python critical_path.py`
   2. Or, pass in in paths to your own input and output locations using
`python critical_path.py -g input/sample_graph.dot -w input/sample_weights.csv -i ../target`
1. Import into another module and pass the graph and node weights inputs into a new CriticalPath object.  See main() for examples.

Important! The node weights must be int's.  Handle any unit conversions outside of this module.  For example if your weights are measured in fractional hours like 2.25 and you want to keep the values precise, convert them to minutes (2.25 * 60), or seconds (2.25 * 60 * 60).  Then the output units will be based on the input units.

# Features

1. Read a graph of tasks from a dotviz file, networkx DiGraph, or a list of tuples
1. Read a the node weights from csv input or a dictionary
1. Return the critical path weighted edges as a dictionary of tuples, with the edge weights as the values
1. Save an image of the graph with the critical path highlighted

# CLI Arguments

* -g, --graph: path to the graph .dot file
* -w, --weights: path to the node weight mapping in csv format
* -i, --image-target: path to where the graph image is saved in png format
* --help: view the help menu

# Testing

TODO: confirm run `python -m pytest`

# Credits

* Dot file example: https://www.graphviz.org/pdf/dotguide.pdf
* Production Operations Management, {TODO: Get book details}

# 