# BotV2 Production Dockerfile - Complete Rewrite
# Multi-stage build optimized for Alpine Linux
# Python 3.11 + Enterprise Grade

# ============================================================================
# Stage 1: Builder - Compile all dependencies
# ============================================================================
FROM python:3.11-alpine as builder

LABEL stage=builder description="Builder stage - compiles all Python packages"

WORKDIR /build

# Install complete build toolchain for Alpine
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
    && echo "[BUILD] pip upgraded to latest version"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies directly to site-packages
# This avoids --user issues and ensures packages are found
RUN echo "[BUILD] Installing Python dependencies..." && \
    pip install --no-cache-dir \
    --prefer-binary \
    -r requirements.txt && \
    echo "[BUILD] ✅ All dependencies installed successfully" && \
    pip list | head -20

# Verify key packages exist in builder
RUN echo "[BUILD] Verifying installations..." && \
    python -c "import pip; print(f'pip: {pip.__version__}')" && \
    python -c "import flask; print(f'✅ Flask available')" && \
    python -c "import dash; print(f'✅ Dash available')" && \
    python -c "import pandas; print(f'✅ Pandas available')" && \
    python -c "import numpy; print(f'✅ NumPy available')"

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
    echo "[RUNTIME] User 'botv2' created with UID 1000"

# Create application directories
RUN mkdir -p /app/{logs,backups,data,config} && \
    chown -R botv2:botv2 /app && \
    echo "[RUNTIME] Application directories created"

# Copy Python packages from builder
# This copies the entire site-packages directory
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=botv2:botv2 src/ ./src/
COPY --chown=botv2:botv2 tests/ ./tests/
COPY --chown=botv2:botv2 .env.example ./
COPY --chown=botv2:botv2 README.md ./

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

# Final verification in runtime stage
RUN echo "[RUNTIME] Final verification of packages..." && \
    python --version && \
    python -c "import sys; print(f'Site-packages: {sys.path}')" && \
    python -c "import flask; print('✅ Flask loaded in runtime')" && \
    python -c "import dash; print('✅ Dash loaded in runtime')" && \
    python -c "import pandas; print('✅ Pandas loaded in runtime')" && \
    python -c "import numpy; print('✅ NumPy loaded in runtime')" && \
    python -c "import psycopg2; print('✅ psycopg2 loaded in runtime')" && \
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
