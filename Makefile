.PHONY: help lint test docs

help:
	@echo "Targets: lint, test, docs"

lint:
	@echo "Run linters here (flake8/ruff/black) once code is added."

test:
	@echo "Run unit tests here (pytest) once code is added."

docs:
	@echo "Build MkDocs site"
	mkdocs build
