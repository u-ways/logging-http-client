################################################################################################
# Project's Makefile
#
# This Makefile is split into the following sections:
#   - Requirements: prerequisites for running the environment.
#   - Application: for building, testing, and publishing the project.
#   - Development: for formatting, linting, and other development tasks.
#   - Docker: for building, running, and publishing Docker images.
#
# We write our rule names in the following format: [verb]-[noun]-[noun], e.g. "build-app".
#
# Variables ####################################################################################

PROJECT_ROOT:=$(CURDIR)
PYTHON_VERSION:=`cat .python-version`

APP_VERSION?=DEV-SNAPSHOT
APP_NAME?=logging-http-client
SRC_DIR?=logging_http_client

IMAGE_ID?=$(APP_NAME):$(APP_VERSION)
IMAGE_SAVE_LOCATION?=$(PROJECT_ROOT)/build/images

# Requirements ##################################################################################

.PHONY: require-pyenv
require-pyenv:
	@command -v pyenv >/dev/null 2>&1 || (echo "Pyenv is required. Please install via 'make install-pyenv'." && exit 1)

.PHONY: require-poetry
require-poetry:
	@command -v poetry >/dev/null 2>&1 || (echo "Poetry is required. Please install via 'make install-poetry'." && exit 1)

.PHONY: require-docker
require-docker:
	@command -v docker >/dev/null 2>&1 || (echo "Docker is required. Please install via https://docs.docker.com/engine/install/." && exit 1)

.PHONY: install-pyenv
install-pyenv:
	@echo "Installing Pyenv..."
	@curl https://pyenv.run | bash

.PHONY: install-poetry
install-poetry:
	@echo "Installing Poetry..."
	@curl -sSL https://install.python-poetry.org | python3 -

# Application ##################################################################################

.PHONY: setup
setup: require-poetry require-pyenv
	@echo "Setting up the project..."
	@echo "Setting local shell Python version to $(PYTHON_VERSION)..."
	@pyenv install -s $(PYTHON_VERSION)
	@pyenv local $(PYTHON_VERSION)
	@poetry config virtualenvs.prefer-active-python true
	@echo "Installing Poetry dependencies..."
	@poetry install
	@echo "Setup complete."
	@echo "Your virtual environment python path is:"
	@echo "$$(poetry env info --path)/bin/python"

.PHONY: test
test:
	@echo "Running tests..."
	@poetry run pytest -s -v $(PROJECT_ROOT)/tests

# Development ##################################################################################

.PHONY: clean
clean:
	@echo "Cleaning application (e.g. cache, build files, virtual environment)..."
	@poetry run pyclean -v ./$(SRC_DIR) ./tests
	@poetry env remove $$(basename $$(poetry env info --path))
	@echo "Cleaning complete."
	@echo "Running 'make setup' to setup the project again."
	@echo "NOTE: For PyCharm users, you might need to attach the new Poetry interpreter to the project."
	@$(MAKE) setup

.PHONY: update-dependencies
update-dependencies:
	@echo "Updating dependencies..."
	@poetry update

.PHONY: lock-dependencies
lock-dependencies:
	@echo "Locking dependencies..."
	@poetry lock

.PHONY: format-code
format-code:
	@echo "Formatting application..."
	@poetry run black $(PROJECT_ROOT)/$(SRC_DIR) $(PROJECT_ROOT)/tests

.PHONY: lint-code
lint-code:
	@echo "Linting application..."
	@poetry run flake8 $(PROJECT_ROOT)/$(SRC_DIR) $(PROJECT_ROOT)/tests

.PHONY: check-format
check-format:
	@echo "Checking application formatting..."
	@poetry run black --check $(PROJECT_ROOT)/$(SRC_DIR) $(PROJECT_ROOT)/tests

.PHONY: check-lint
check-lint:
	@echo "Checking application linting..."
	@poetry run flake8 --show-source --statistics --count $(PROJECT_ROOT)/$(SRC_DIR) $(PROJECT_ROOT)/tests

.PHONY: enable-code-quality-pre-commit-hook
enable-code-quality-pre-commit-hook:
	@echo "Enabling pre-commit hook..."
	@ln -sf $(PROJECT_ROOT)/.hooks/pre-commit $(PROJECT_ROOT)/.git/hooks/pre-commit
	@echo "Pre-commit hook enabled."

.PHONE: disable-code-quality-pre-commit-hook
disable-code-quality-pre-commit-hook:
	@echo "Disabling pre-commit hook..."
	@rm -f $(PROJECT_ROOT)/.git/hooks/pre-commit
	@echo "Pre-commit hook disabled."

# Docker #######################################################################################

.PHONY: check-test-docker
check-test-docker: require-docker
	@echo "Testing application... (Containerised)"
	@$(call build_docker_image,development)
	@$(call run_docker_dev_mount,poetry run pytest -v /app/tests)

.PHONY: check-format-docker
check-format-docker: require-docker
	@echo "Checking application formatting... (Containerised)"
	@$(call build_docker_image,development)
	@$(call run_docker_dev_mount,poetry run black --check /app/$(SRC_DIR) /app/tests)

.PHONY: check-lint-docker
check-lint-docker: require-docker
	@echo "Checking application linting... (Containerised)"
	@$(call build_docker_image,development)
	@$(call run_docker_dev_mount,poetry run flake8 --show-source --statistics --count /app/$(SRC_DIR) /app/tests)

.PHONY: check-code-quality-docker
check-code-quality-docker: require-docker
	@echo "Checking application code quality... (Containerised)"
	@$(MAKE) check-format-docker
	@$(MAKE) check-lint-docker
	@$(MAKE) check-test-docker

# Functions ####################################################################################

define build_docker_image
	@echo "Building Docker image for target: $(1)"
	@docker build --target $(1) --build-arg APP_VERSION=$(APP_VERSION) --build-arg APP_NAME=$(APP_NAME) -t $(IMAGE_ID) .
endef

define run_docker_dev_mount
	@docker run $(2) \
		--network=host \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_ROOT)/$(SRC_DIR):/app/$(SRC_DIR) \
		-v $(PROJECT_ROOT)/tests:/app/tests \
		-v $(PROJECT_ROOT)/pyproject.toml:/app/pyproject.toml \
		-v $(PROJECT_ROOT)/poetry.lock:/app/poetry.lock \
		--rm --name $(APP_NAME)-toolchain-dev $(IMAGE_ID) $(1)
endef
