ps:
	docker ps

cli:
	docker exec -ti critical-path-finder_web_1 sh 

test:
	python -m pytest
