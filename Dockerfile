# An optimised multistaged Dockerfile for Poetry.
# Based of https://github.com/python-poetry/poetry/discussions/1879?sort=top#discussioncomment-216865

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.12-slim as python-base
LABEL python-base=true

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # see: https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    # paths this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    # where the virtual environment will be created
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base
LABEL builder-base=true

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# Installs poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

# Switch to the directory with our poetry files
WORKDIR $PYSETUP_PATH

# Copy project requirement files here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install --without dev,test --no-root


################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM python-base as development
LABEL development=true

ENV FASTAPI_ENV=development
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Switch to the directory with our poetry files
WORKDIR $PYSETUP_PATH

# It's important to note that the development stage does not
# include the project source code. (i.e. you're responsible
# for volume mounting the code when you run the container as
# development source shouldn't be part of the image)

# Copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    poetry install --with dev,test

WORKDIR /app