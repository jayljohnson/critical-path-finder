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
1. Return the critical path weighted edges as a dictionary of tuples, with the edge weights as values
1. Save an image of the graph with the critical path highlighted

# Credits
* Dot file example: https://www.graphviz.org/pdf/dotguide.pdf
* Production Operations Management, {TODO: Get book details}
