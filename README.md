# Usage

1. Clone the package into a local directory
1. Run as a script. Options:
   1. Using the provided sample inputs with `python critical_path.py`
   2. Or pass in paths to your own input and output locations using
`python critical_path.py -g input/sample_graph.dot -w input/sample_weights.csv -i ../target`
1. View the output image of the graph

## Generating a dotviz graph .dot file
1. Airflow cli:  `airflow dags show <DAG_ID> –save output.dot`

# Features

## Inputs
1. Read a graph of tasks from a dotviz file
1. Read a csv input containing the list tasks with their execution time

## Arguments
* -g: path to the graph .dot file
* -f: path to the node weight mapping in csv format
* -i: path to where the graph image is saved in png format

## Outputs
1. Return the critical path nodes the graph, using the execution time as the edge weights of the graph
1. Save an image of the graph with the critical path highlighted

# Backlog
1. Layout the graph in left-to-right format, so that edge arrows are always directed towards the right
1. Render the graph image and critical path edge list in a django app
    1. With static inputs
    1. With user-submitted inputs
1. Store user-submitted input and results

# Credits
* Dot file example: https://www.graphviz.org/pdf/dotguide.pdf
* Production Operations Management, {TODO: Get book details}
