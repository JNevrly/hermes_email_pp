FROM python:3.13-slim

# Install git and other dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install OpenCode CLI
RUN curl -fsSL https://opencode.ai/install | bash
