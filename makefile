ps:
	docker ps

cli:
	# docker exec -it f086c070d28a  /bin/bash
	docker exec -ti critical-path-finder_web_1 sh 

test:
	python -m pytest
