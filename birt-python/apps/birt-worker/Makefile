# ----------------------------------------
# UNIT TESTS
# ----------------------------------------

.PHONY: ut
ut:
	@echo "> Running unit tests"
	uv run pytest ./tests/ut

# ----------------------------------------
# INTEGRATION TESTS
# ----------------------------------------

.PHONY: it
it:
	@echo "> Running integration tests"
	uv run pytest ./tests/it

# ----------------------------------------
# CODE QUALITY
# ----------------------------------------

.PHONY: check
check: check-ruff-formatter check-ruff-linter check-mypy

# Ruff

.PHONY: fmt
fmt:
	@echo "> Sorting imports"
	uv run ruff check --select I --fix .
	@echo "> Formatting code"
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: check-ruff-formatter
check-ruff-formatter:
	@echo "> Checking import order"
	uv run ruff check --select I .
	@echo "> Checking format"
	uv run ruff format --check .

.PHONY: check-ruff-linter
check-ruff-linter:
	@echo "> Linting code"
	uv run ruff check .

# Mypy

.PHONY: check-mypy
check-mypy:
	@echo "> Checking types"
	uv run mypy .
