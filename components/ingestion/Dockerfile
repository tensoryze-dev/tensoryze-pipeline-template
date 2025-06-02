
# Define base image
FROM python:3.10-slim as base

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Build stage for cloning the repository
FROM base as builder

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv $VIRTUAL_ENV

WORKDIR /code

ARG GITHUB_INSTALL_TOKEN


COPY requirements.txt .

# install dependencies
RUN pip install git+https://${GITHUB_INSTALL_TOKEN}@github.com/tensoryze-dev/tensoryze_pipelines.git#egg=tensoryze_pipelines && \
    pip install -r requirements.txt && \
    rm -rf ~/.cache/pip


COPY app.py .
COPY .env .

CMD ["python", "./app.py"]
