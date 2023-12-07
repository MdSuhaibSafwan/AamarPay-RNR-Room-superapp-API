FROM python:3.9


ARG ENV_ARG

RUN echo $ENV_ARG

ENV ENV_ARG=${ENV_ARG} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7.0


# System Deps
RUN pip install "poetry==$POETRY_VERSION"

# Cache Only Requirements To Cache Them In Docker Layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project Initialization
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_ARG" == production && echo "--no-dev") --no-interaction --no-ansi

# Coping Folders and Files For Project
COPY . /app/

# Make Deployment Script Executable
RUN sed -i 's/\r$//g' /app/deployment/*
RUN chmod +x /app/deployment/*
ENTRYPOINT ["/app/deployment/entrypoint"]
