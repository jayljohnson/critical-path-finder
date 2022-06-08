# Features

1. Read a dotviz file into a networx directed acyclic graph representing a graph of tasks
    1. Add the airflow cli command to get the dotviz output 
1. Read a csv input containing the list tasks with their execution time
1. Return the critical path nodes the graph, using the execution time as the edge weights
1. Assign a color to the critical path edges
1. Return an image of the graph with the critical path highlighted

# Backlog
1. Layout the graph in left-to-right format, so that edge arrows are always directed towards the right
1. Render the graph image and critical path edge list in a django app
    1. With static inputs
    1. With user-submitted inputs
1. Store user-submitted input and results
1. Render the edge weights
1. Render the node start and end timestamp info
