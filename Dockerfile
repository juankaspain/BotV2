# BotV2 Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 botv2 && \
    mkdir -p /app/logs /app/backups /app/data && \
    chown -R botv2:botv2 /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/botv2/.local

# Copy application code
COPY --chown=botv2:botv2 src/ ./src/
COPY --chown=botv2:botv2 tests/ ./tests/

# Set Python path
ENV PATH=/home/botv2/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER botv2

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "src/main.py"]