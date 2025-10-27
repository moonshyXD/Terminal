PYTHON = python3

.PHONY: lint
lint:
	@echo "Запуск линтера"
	ruff format .
	ruff check --fix
	mypy .

.PHONY: run
run:
	$(PYTHON) -m src.main
