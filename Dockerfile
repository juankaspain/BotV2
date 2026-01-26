# BotV2 Production Dockerfile - Enterprise Grade
# Multi-stage build optimized for Alpine Linux
# Python 3.11 + all wheels pre-built
# VERIFIED: Tested and working without compilation errors
# OPTIMIZED: Cleaned __pycache__, fixed casing, minimal output

# ============================================================================
# Stage 1: Builder - Compile all dependencies
# ============================================================================
FROM python:3.11-alpine AS builder

LABEL stage=builder description="Builder stage - installs all Python packages"

WORKDIR /build

# Install complete build toolchain for Alpine
# Only used during pip install, removed in runtime stage
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    git \
    python3-dev \
    && echo "[BUILD] Complete build toolchain installed"

# Upgrade pip, setuptools, wheel FIRST
RUN pip install --upgrade --no-cache-dir \
    pip \
    setuptools \
    wheel \
    && echo "[BUILD] pip, setuptools, wheel upgraded"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to system site-packages
# KEY FLAGS:
#   --no-cache-dir: Don't cache pip packages (saves space)
#   --prefer-binary: Use pre-built wheels when available (faster, more reliable)
#   --only-binary=:all:: Force wheels only, fail if not available (Alpine-safe)
# This ensures all packages use pre-built wheels instead of compiling from source
RUN echo "[BUILD] Installing Python dependencies..." && \
    pip install --no-cache-dir \
    --prefer-binary \
    --only-binary=:all: \
    -r requirements.txt && \
    echo "[BUILD] ✅ All dependencies installed successfully"

# Cleanup __pycache__ to reduce image size
RUN find /usr/local -type f -name '*.pyc' -delete && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    echo "[BUILD] Cache cleaned"

# Verify core packages exist in builder
RUN echo "[BUILD] Verifying installations..." && \
    python -c "import pip; print(f'pip: {pip.__version__}')" && \
    python -c "import flask; print('✅ Flask')" && \
    python -c "import dash; print('✅ Dash')" && \
    python -c "import pandas; print('✅ Pandas')" && \
    python -c "import numpy; print('✅ NumPy')" && \
    echo "[BUILD] ✅ All core packages verified"

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-alpine

LABEL maintainer="Juan Carlos Garcia <juanca755@hotmail.com>"
LABEL description="BotV2 Trading System - Enterprise Grade"
LABEL version="4.1"

WORKDIR /app

# Install ONLY runtime dependencies (no build tools)
RUN apk add --no-cache \
    libpq \
    curl \
    ca-certificates \
    tini \
    && echo "[RUNTIME] Runtime dependencies installed"

# Create non-root user for security
RUN addgroup -g 1000 botv2 && \
    adduser -u 1000 -G botv2 -s /sbin/nologin -D botv2 && \
    echo "[RUNTIME] User 'botv2' created"

# Create application directories
RUN mkdir -p /app/{logs,backups,data,config} && \
    chown -R botv2:botv2 /app && \
    echo "[RUNTIME] Directories created"

# Copy Python site-packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy Python bin (pip, etc)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=botv2:botv2 src/ ./src/
COPY --chown=botv2:botv2 bot/ ./bot/
COPY --chown=botv2:botv2 dashboard/ ./dashboard/
COPY --chown=botv2:botv2 tests/ ./tests/
COPY --chown=botv2:botv2 .env.example ./
COPY --chown=botv2:botv2 README.md ./

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

# Final verification in runtime stage
RUN echo "[RUNTIME] Final verification..." && \
    python --version && \
    python -c "import flask; print('✅ Flask')" && \
    python -c "import dash; print('✅ Dash')" && \
    python -c "import pandas; print('✅ Pandas')" && \
    python -c "import numpy; print('✅ NumPy')" && \
    python -c "import psycopg2; print('✅ psycopg2')" && \
    echo "[RUNTIME] ✅ All verifications passed"

# Switch to non-root user
USER botv2

# Use tini as PID 1 for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import flask, dash, pandas, numpy; exit(0)" || exit 1

# Default command
CMD ["python", "src/main.py"]
