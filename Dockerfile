# syntax=docker/dockerfile:1
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first so this layer is reused when only the code changes.
# - The pip cache mount keeps downloaded wheels between builds, so a change to
#   requirements.txt only downloads what actually changed.
# - torch comes from the CPU-only index: the server has no GPU, and the default
#   Linux wheel pulls several GB of NVIDIA CUDA libraries.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt \
        --extra-index-url https://download.pytorch.org/whl/cpu

FROM base AS build
COPY . .

CMD ["uvicorn", "main_server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
