# Stage 1: Build stage
FROM python:3.9-slim-bookworm as builder

WORKDIR /app

COPY requirements.txt .

# A single, simple install step
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
