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

# Copy application
COPY app.py .

# Create non-root user (important security hardening)
RUN useradd -m appuser
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
