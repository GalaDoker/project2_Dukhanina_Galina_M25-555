install:
	poetry install

run:
	poetry run database

project:
	poetry run database

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*

lint:
	poetry run ruff check .
