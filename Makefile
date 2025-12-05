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
# MODEL GENERATION (OpenAPI -> Pydantic)
# =============================================================================
# Generates Pydantic models from OpenAPI spec packaged as npm .tgz artifact
#
# Workflow:
#   1. OpenAPI spec is npm-packed into a .tgz (from artifactory or local)
#   2. This Makefile extracts the spec and runs datamodel-codegen
#   3. Pydantic models are generated into src/.../models/
#
# Usage:
#   make generate-models SPEC_TGZ=path/to/spec.tgz
#   make generate-models-url SPEC_URL=https://artifactory.../spec.tgz

# Configuration
SPEC_TGZ ?= openapi-spec.tgz
SPEC_URL ?=
MODELS_DIR := src/marketing_connect_mcp_services/models
SPEC_EXTRACT_DIR := .tmp/openapi-spec
SPEC_FILE_NAME ?= mcpservices-api.yml

# datamodel-codegen executable (installed via codegen extra)
DATAMODEL_CODEGEN := $(UV) run datamodel-codegen

.PHONY: generate-models
generate-models: ## Generate Pydantic models from local OpenAPI spec .tgz
	@echo "==> Generating models from $(SPEC_TGZ)..."
	@if [ ! -f "$(SPEC_TGZ)" ]; then \
		echo "Error: $(SPEC_TGZ) not found"; \
		echo "Usage: make generate-models SPEC_TGZ=path/to/openapi-spec.tgz"; \
		exit 1; \
	fi
	@mkdir -p $(SPEC_EXTRACT_DIR)
	@echo "==> Extracting OpenAPI spec..."
	@tar -xzf $(SPEC_TGZ) -C $(SPEC_EXTRACT_DIR)
	@SPEC_PATH=$$(find $(SPEC_EXTRACT_DIR) -name "$(SPEC_FILE_NAME)" -o -name "*.yaml" -o -name "*.yml" | head -1); \
	if [ -z "$$SPEC_PATH" ]; then \
		echo "Error: No OpenAPI spec found in $(SPEC_TGZ)"; \
		echo "Looking for: $(SPEC_FILE_NAME) or any .yaml/.yml file"; \
		rm -rf $(SPEC_EXTRACT_DIR); \
		exit 1; \
	fi; \
	echo "==> Found spec: $$SPEC_PATH"; \
	echo "==> Running datamodel-codegen..."; \
	mkdir -p $(MODELS_DIR); \
	$(DATAMODEL_CODEGEN) \
		--input "$$SPEC_PATH" \
		--input-file-type openapi \
		--output $(MODELS_DIR)/models.py \
		--output-model-type pydantic_v2.BaseModel \
		--use-schema-description \
		--field-constraints \
		--use-double-quotes \
		--target-python-version 3.11; \
	echo "# Generated models - do not edit manually" > $(MODELS_DIR)/__init__.py; \
	echo "from .models import *" >> $(MODELS_DIR)/__init__.py
	@rm -rf $(SPEC_EXTRACT_DIR)
	@echo "==> Models generated: $(MODELS_DIR)/models.py"

.PHONY: generate-models-url
generate-models-url: ## Generate models from OpenAPI spec at URL (set SPEC_URL)
	@if [ -z "$(SPEC_URL)" ]; then \
		echo "Error: SPEC_URL not set"; \
		echo "Usage: make generate-models-url SPEC_URL=https://artifactory.../openapi-spec.tgz"; \
		exit 1; \
	fi
	@echo "==> Fetching spec from $(SPEC_URL)..."
	@curl -fsSL "$(SPEC_URL)" -o /tmp/openapi-spec.tgz
	@$(MAKE) generate-models SPEC_TGZ=/tmp/openapi-spec.tgz
	@rm -f /tmp/openapi-spec.tgz

.PHONY: generate-models-local
generate-models-local: ## Generate models from local OpenAPI spec file (set SPEC_FILE)
	@if [ -z "$(SPEC_FILE)" ]; then \
		echo "Error: SPEC_FILE not set"; \
		echo "Usage: make generate-models-local SPEC_FILE=path/to/openapi.yaml"; \
		exit 1; \
	fi
	@echo "==> Generating models from $(SPEC_FILE)..."
	@mkdir -p $(MODELS_DIR)
	$(DATAMODEL_CODEGEN) \
		--input "$(SPEC_FILE)" \
		--input-file-type openapi \
		--output $(MODELS_DIR)/models.py \
		--output-model-type pydantic_v2.BaseModel \
		--use-schema-description \
		--field-constraints \
		--use-double-quotes \
		--target-python-version 3.11
	@echo "# Generated models - do not edit manually" > $(MODELS_DIR)/__init__.py
	@echo "from .models import *" >> $(MODELS_DIR)/__init__.py
	@echo "==> Models generated: $(MODELS_DIR)/models.py"

.PHONY: models-clean
models-clean: ## Remove generated models
	@echo "Cleaning generated models..."
	@rm -f $(MODELS_DIR)/models.py 2>/dev/null || true
	@echo "Generated models removed"

.PHONY: models-show
models-show: ## Show generated model classes
	@echo "Generated models in $(MODELS_DIR)/models.py:"
	@grep "^class " $(MODELS_DIR)/models.py 2>/dev/null || echo "No models found"

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
	@echo "  make build                    # Install dependencies"
	@echo "  make run                      # Start the server"
	@echo "  make test                     # Run tests"
	@echo ""
	@echo "Model Generation:"
	@echo "  make generate-models SPEC_TGZ=spec.tgz        # From local .tgz"
	@echo "  make generate-models-url SPEC_URL=https://... # From artifactory URL"
	@echo "  make generate-models-local SPEC_FILE=api.yml  # From local YAML"
	@echo ""
	@echo "Environment Variables:"
	@echo "  UV_INDEX_URL   # Override PyPI index (set in pyproject.toml)"
	@echo "  SPEC_TGZ       # Path to OpenAPI spec .tgz (default: openapi-spec.tgz)"
	@echo "  SPEC_URL       # URL to fetch OpenAPI spec .tgz"
	@echo "  SPEC_FILE_NAME # Name of spec file in .tgz (default: mcpservices-api.yml)"
	@echo ""
