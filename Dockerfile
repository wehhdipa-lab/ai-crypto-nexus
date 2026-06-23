FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml setup.py ./
COPY src/ src/
RUN pip install --no-cache-dir .

FROM base AS dev
RUN pip install --no-cache-dir ".[dev]"
COPY tests/ tests/
CMD ["pytest", "-v"]
