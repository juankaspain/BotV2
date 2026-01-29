# BotV2 Production Dockerfile - Enterprise Grade
# Multi-stage build optimized for Alpine Linux
# Python 3.11 + compilation support for ML packages
# VERIFIED: Tested and working with scikit-learn
# Last updated: 27-01-2026

# ============================================================================
# Stage 1: Builder - Compile all dependencies
# ============================================================================
FROM python:3.14-alpine AS builder

LABEL stage=builder description="Builder stage - installs all Python packages"

WORKDIR /build

# Install complete build toolchain for Alpine
# Required for: scikit-learn, scipy, cryptography, psycopg2
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
    openblas-dev \
    lapack-dev \
    gfortran \
    && echo "[BUILD] Complete build toolchain installed"

# Upgrade pip, setuptools, wheel FIRST
RUN pip install --upgrade --no-cache-dir \
    pip \
    setuptools \
    wheel \
    Cython \
    && echo "[BUILD] pip, setuptools, wheel, Cython upgraded"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# --prefer-binary: Use wheels when available, compile when needed
# NO --only-binary: Allow compilation for packages without musllinux wheels
RUN echo "[BUILD] Installing Python dependencies (this may take several minutes)..." && \
    pip install --no-cache-dir \
    --prefer-binary \
    -r requirements.txt && \
    echo "[BUILD] ✅ All dependencies installed successfully"

# Cleanup __pycache__ and build artifacts
RUN find /usr/local -type f -name '*.pyc' -delete && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /root/.cache/pip && \
    echo "[BUILD] Cache cleaned"

# Verify core packages
RUN echo "[BUILD] Verifying installations..." && \
    python -c "import pip; print(f'pip: {pip.__version__}')" && \
    python -c "import flask; print('✅ Flask')" && \
    python -c "import dash; print('✅ Dash')" && \
    python -c "import pandas; print('✅ Pandas')" && \
    python -c "import numpy; print('✅ NumPy')" && \
    python -c "import sklearn; print('✅ scikit-learn')" && \
    echo "[BUILD] ✅ All core packages verified"

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.14-alpine

LABEL maintainer="Juan Carlos Garcia <juanca755@hotmail.com>"
LABEL description="BotV2 Trading System - Enterprise Grade"
LABEL version="5.1"

WORKDIR /app

# Install ONLY runtime dependencies
# libopenblas needed for scikit-learn/numpy at runtime
RUN apk add --no-cache \
    libpq \
    libstdc++ \
    libgomp \
    openblas \
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
COPY --chown=botv2:botv2 main.py ./
COPY --chown=botv2:botv2 bot/ ./bot/
COPY --chown=botv2:botv2 dashboard/ ./dashboard/
COPY --chown=botv2:botv2 shared/ ./shared/
COPY --chown=botv2:botv2 config.yaml ./
COPY --chown=botv2:botv2 .env.example ./
COPY --chown=botv2:botv2 README.md ./

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

# Final verification
RUN echo "[RUNTIME] Final verification..." && \
    python --version && \
    python -c "import flask; print('✅ Flask')" && \
    python -c "import dash; print('✅ Dash')" && \
    python -c "import pandas; print('✅ Pandas')" && \
    python -c "import numpy; print('✅ NumPy')" && \
    python -c "import sklearn; print('✅ scikit-learn')" && \
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
CMD ["python", "main.py"]
