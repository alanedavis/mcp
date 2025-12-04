# =============================================================================
# Makefile - Marketing Connect MCP Services
# =============================================================================
# Uses uv for fast Python package management
# https://github.com/astral-sh/uv
# =============================================================================

UV_VERSION := 0.5.5
SSAP_DIR := ssap_bill_of_materials
VENV := .venv
PYTHON := $(VENV)/Scripts/python
UV := uv

.PHONY: all
.DEFAULT_GOAL=help

# =============================================================================
# MCP SERVER COMMANDS
# =============================================================================

.PHONY: run
run: ## Start the MCP server (default: 0.0.0.0:8000)
	$(UV) run marketing-connect-mcp

.PHONY: run-debug
run-debug: ## Start the MCP server in debug mode
	MCP_DEBUG=true MCP_LOG_LEVEL=DEBUG $(UV) run marketing-connect-mcp

.PHONY: run-dev
run-dev: ## Start the MCP server on localhost only (port 8000)
	$(UV) run marketing-connect-mcp --host 127.0.0.1

# =============================================================================
# BUILD & INSTALL
# =============================================================================

.PHONY: clean
clean: ## Remove all cache, reports, coverage, distribution files and folders
	rm -f .coverage
	rm -f requirements.txt
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf reports
	rm -rf $(SSAP_DIR)
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf *.egg-info
	rm -rf src/*.egg-info

.PHONY: distclean
distclean: clean ## Remove all build and test artifacts and the virtual environment
	rm -rf $(VENV)
	rm -f uv.lock

.PHONY: venv
venv: ## Create virtual environment
	$(UV) venv $(VENV)

.PHONY: build
build: ## Create the virtual environment and install all dependencies
	$(UV) sync --all-extras

.PHONY: build-prod
build-prod: ## Install production dependencies only (no dev/test)
	$(UV) sync --no-dev

.PHONY: update
update: ## Update dependencies to latest versions
	$(UV) lock --upgrade
	$(UV) sync --all-extras

.PHONY: lock
lock: ## Generate/update uv.lock file
	$(UV) lock

# =============================================================================
# TESTING & QUALITY
# =============================================================================

.PHONY: test
test: ## Execute test cases
	$(UV) run pytest

.PHONY: test-verbose
test-verbose: ## Execute test cases with verbose output
	$(UV) run pytest -v

.PHONY: precommit
precommit: ## Run pre-commit hooks on all files
	$(UV) run pre-commit install
	$(UV) run pre-commit run --all-files

.PHONY: cover
cover: ## Execute test cases and produce coverage reports
	mkdir -p reports
	$(UV) run pytest --cov src/ --junitxml reports/xunit.xml \
	  --cov-report xml:reports/coverage.xml --cov-report term-missing

.PHONY: format
format: ## Formats the Python Files
	$(UV) run ruff format .

.PHONY: lint
lint: ## Lint all files
	$(UV) run ruff check .

.PHONY: lint-fix
lint-fix: ## Lint and auto-fix all files
	$(UV) run ruff check --fix .

.PHONY: typecheck
typecheck: ## Run type checking with mypy
	$(UV) run mypy src/

.PHONY: check
check: lint typecheck test ## Run all checks (lint, typecheck, test)

# =============================================================================
# CI/CD & PACKAGING
# =============================================================================

.PHONY: ssap
ssap: ## Generates requirements.txt file and required reports for SSAP
	mkdir -p $(SSAP_DIR)
	$(UV) pip compile pyproject.toml -o $(SSAP_DIR)/pip_dependency_tree.txt

.PHONY: ci-prebuild
ci-prebuild: ## Installs uv package manager
	pip install uv==$(UV_VERSION)

.PHONY: package
package: ## Create deployable whl packages for python project
	$(UV) build --wheel

.PHONY: ci
ci: clean build test package ## Runs clean, build, test, and package

# =============================================================================
# HELP
# =============================================================================

.PHONY: help
help: ## Show make target documentation
	@echo ""
	@echo "Marketing Connect MCP Server"
	@echo "============================"
	@echo "Build system: Hatchling + uv"
	@echo ""
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Quick Start:"
	@echo "  make build    # Install dependencies"
	@echo "  make run      # Start the server"
	@echo "  make test     # Run tests"
	@echo ""
	@echo "Environment Variables:"
	@echo "  UV_INDEX_URL  # Override PyPI index (set in pyproject.toml)"
	@echo ""
