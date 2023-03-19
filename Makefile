.PHONY: setup clean lint test load
SHELL := /bin/bash

setup:
	docker-compose up

clean:
	docker-compose stop; \
	docker-compose down --remove-orphans; \
	docker image prune -f; \
	find . -type d -name '*cache*' -prune -exec rm -rf {} +

lint:
	docker-compose run --rm api /bin/bash -c "black .; ruff . --fix"

test:
	docker-compose run --rm api /bin/bash -c "pytest -vv ."

load:
	./loadtest/run.sh
