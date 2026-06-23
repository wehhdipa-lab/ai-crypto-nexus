# =============================================================================
# AI Crypto Nexus — Multi-stage Docker Build
# Stage 1: Builder (compile dependencies)
# Stage 2: Runtime (minimal production image)
# =============================================================================

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency files first for layer caching
COPY pyproject.toml setup.py README.md ./
COPY src/nexus/__init__.py src/nexus/

# Install dependencies
RUN pip install --prefix=/install .

# Copy source
COPY src/ src/

# Install the package
RUN pip install --prefix=/install .


# --- Stage 2: Runtime ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:${PATH}" \
    LD_LIBRARY_PATH="/install/lib:${LD_LIBRARY_PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nexus && useradd -r -g nexus -d /app -s /sbin/nologin nexus

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ src/
COPY .env.example ./

# Create directories
RUN mkdir -p /app/keystore /app/data /app/logs && \
    chown -R nexus:nexus /app

USER nexus

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import nexus; print('ok')" || exit 1

EXPOSE 8080

# Use tini for proper signal handling
ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "nexus.cli", "run"]
