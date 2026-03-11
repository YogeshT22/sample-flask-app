# Builder stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.12-slim-bookworm

# Update OS packages to latest security patches
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy gunicorn binary from builder
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application
COPY app.py .

# Create non-root user with explicit UID=1001
# Numeric UID is required for Kubernetes runAsNonRoot enforcement —
# K8s validates by UID at admission time, not by username string.
RUN useradd -u 1001 -m appuser
USER 1001

EXPOSE 5000

# Use gunicorn production WSGI server instead of Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
