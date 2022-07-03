all: run

ps:
	docker ps

cli:
	docker exec -ti critical-path-finder_web_1 sh

run:
	# TODO: Not working from makefile, works manually
	python critical_path_finder/critical_path_finder.py -g input/sample_graph.dot -w input/sample_weights.csv -i ../target

test:
	python -m pytest
