# ===================================
# 🛡️ Agentic Honey-Pot API - Dockerfile
# Multi-stage build for production deployment
# ===================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    whois \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 honeypot && \
    mkdir -p /app && \
    chown -R honeypot:honeypot /app

WORKDIR /app

# ===================================
# Dependencies Stage
# ===================================
FROM base as dependencies

# Copy requirements first for better caching
COPY --chown=honeypot:honeypot requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ===================================
# Production Stage
# ===================================
FROM base as production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=honeypot:honeypot . .

# Switch to non-root user
USER honeypot

# Expose port (Render will override with $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run with gunicorn for production
CMD gunicorn main:app \
    --workers ${WORKERS:-2} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
