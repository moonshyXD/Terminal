PYTHON = python3

.PHONY: setup
setup:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync

.PHONY: lint
lint:
	@echo "Запуск линтера"
	ruff format .
	ruff check --fix
	mypy .

.PHONY: run
run:
	$(PYTHON) -m main

.PHONY: test
test:
	pytest tests

.PHONY: testcover
testcover:
	pytest --cov=src --cov-report=term-missing
