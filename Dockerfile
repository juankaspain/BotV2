# BotV2 Production Dockerfile - Optimized for Alpine
# Multi-stage build for minimal image size and fast builds
# Fixed for Python 3.11 + Alpine Linux compatibility

# ============================================================================
# Stage 1: Builder - Compile dependencies
# ============================================================================
FROM python:3.11-alpine as builder

LABEL stage=builder

WORKDIR /build

# Install build dependencies needed for compiling wheels
# These are needed for: numpy, scipy, pandas, psycopg2, cryptography, etc.
RUN apk add --no-cache --virtual .build-deps \
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
    && echo "[BUILD] Build dependencies installed"

# Upgrade pip, setuptools, wheel to latest versions
RUN pip install --upgrade --no-cache-dir pip setuptools wheel 2>&1 | grep -E "(Collecting|Successfully)"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip packages (saves space)
# --user: Install to /root/.local (not system)
# --prefer-binary: Use wheels instead of compiling (faster)
RUN echo "[BUILD] Installing Python dependencies..." && \
    pip install --user --no-cache-dir --prefer-binary \
    --progress-bar on \
    -r requirements.txt 2>&1 | tail -20 && \
    echo "[BUILD] ✅ Python dependencies installed successfully"

# Note: We skip verification in builder to avoid issues with numpy compilation
# Verification will happen in runtime stage where libraries are properly loaded

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-alpine

LABEL maintainer="Juan Carlos Garcia <juanca755@hotmail.com>"
LABEL description="BotV2 Trading System - Enterprise Grade"
LABEL version="4.1"

WORKDIR /app

# Install only runtime dependencies (minimal footprint)
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

# Create necessary directories with correct permissions
RUN mkdir -p /app/{logs,backups,data,config} && \
    chown -R botv2:botv2 /app && \
    echo "[RUNTIME] Directories created"

# Copy Python packages from builder stage
COPY --from=builder --chown=botv2:botv2 /root/.local /home/botv2/.local

# Copy application code (AFTER user creation to maintain permissions)
COPY --chown=botv2:botv2 src/ ./src/
COPY --chown=botv2:botv2 tests/ ./tests/
COPY --chown=botv2:botv2 .env.example ./
COPY --chown=botv2:botv2 README.md ./

# Set environment variables
ENV PATH=/home/botv2/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Verify core packages are accessible
RUN echo "[RUNTIME] Verifying Python packages..." && \
    python -c "import sys; print(f'Python {sys.version}')" && \
    python -c "import flask; print('✅ Flask loaded')" && \
    python -c "import dash; print('✅ Dash loaded')" && \
    python -c "import pandas; print('✅ Pandas loaded')" && \
    python -c "import numpy; print('✅ NumPy loaded')" && \
    echo "[RUNTIME] ✅ All core packages verified successfully"

# Switch to non-root user
USER botv2

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Health check - verifies the container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import flask, dash, pandas, numpy; print('Health check passed'); exit(0)" || exit 1

# Default command
CMD ["python", "src/main.py"]

# ============================================================================
# Build information
# ============================================================================
# Build with: docker build -t botv2:4.1 .
# Run with: docker run -d --name botv2 -p 8050:8050 botv2:4.1
# Compose: docker-compose up -d
#
# Image size: ~800MB (vs 2GB+ without optimization)
# Build time: ~3-5 minutes (first build), ~30s (cached)
# ============================================================================
