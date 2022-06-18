# critical-path-finder

Calculate the critical (longest) path within a network (graph) of weighted task dependencies.

Returns the tasks with dependencies and their weights, and the sum of the weights from those tasks.

Used for understanding and optimizing any physical or virtual systems.

## Quick Start

1. Run from the CLI by:
   1. Using the provided sample inputs with `python critical_path_finder.py`
   1. Or, pass in in paths to your own input and output locations using
`python critical_path_finder.py -g input/sample_graph.dot -w input/sample_weights.csv -i ../target`
1. Import into another module and pass the graph and node weights inputs into a new CriticalPath object.  See main() for examples.

Important! The node weights must be int's.  Handle any unit conversions outside of this module.  For example if your weights are measured in fractional hours like 2.25 and you want to keep the values precise, convert them to minutes (2.25 * 60), or seconds (2.25 * 60 * 60).  Then the output units will be based on the input units.

### CLI Arguments

* -g, --graph: path to the graph .dot file
* -w, --weights: path to the node weight mapping in csv format
* -i, --image-target: path to where the graph image is saved in png format
* --help: view the help menu

## Features

1. Read a graph of tasks from one of three sources:
    1. Graphviz digraph file (.dot) by calling `CriticalPath().load_graph_from_dot_file()`
    1. Networkx DiGraph by passing it into the `graph` variable during CriticalPath() instance creation
    1. Python List of tuples representing graph edges by converting it to a NetworkxDigraph by calling static method `CriticalPath()._get_digraph_from_tuples()`, then passing it into the `graph` variable during `CriticalPath()` instance creation.
1. Read the weighting of each graph node from one of two sources:
    1. csv file with two columns, the node and the weight
    1. Python dictionary
1. Return the critical path weighted edges as a dictionary of tuples, with the edge weights as the values
![Example CLI output showing the critical path as weighted edges](/critical_path_finder/sample/CLI-output-sample.png?raw=true "Sample Critical Path Dictionary")
1. Save an image of the graph with the critical path highlighted
![Example graph with the critical path highlighted](/critical_path_finder/sample/CriticalPathGraph-sample.png?raw=true "Sample Critical Path Image")

## Design Assumptions

1. Work is performed as tasks.  Task relationships form a graph or network.
1. The graph is directional and does not repeat (acyclic).  This graph structure is called a DAG, or DiGraph.
1. Tasks are orchestrated according to the dependencies between tasks
1. The network of task dependencies is managed separately than the orchestration history, and the data structures for each are decoupled.  Information about task performance, such as duration or cost, are tracked during task orchestration.
1. The task weight units of measure are varied and could represent time, cost, volume, or something else.  The critical path calculation is agnostic to the unit of measure and accepts any integer value.  Conversion to or from fractional units happens outside of this module.
1. Don't reinvent the wheel.  Focus on ease of use with the inputs and outputs.  Use existing and proven graph theory libraries where possible, including networkx and graphviz.

## Testing

Run `python -m pytest`

## Credits and References

* For more info on CPM see https://en.wikipedia.org/wiki/Critical_path_method.
* The .dot file sample is based on the example in the Graphviz docs: https://www.graphviz.org/pdf/dotguide.pdf
* Production Operations Management is the scientific study of business and production systems
