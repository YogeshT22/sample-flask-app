# flow is:
# 1. Build the Docker image
# 2. Push the image to the local registry
# 3. Deploy the image to the K3s cluster

FROM python:3.9-slim-bookworm as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
