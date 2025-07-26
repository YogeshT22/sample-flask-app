# Stage 1: Use a standard Python image to install dependencies
FROM python:3.9-slim-bookworm as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Use a smaller base image for the final application
FROM python:3.9-bookworm-slim
WORKDIR /app
# Copy installed dependencies from the 'builder' stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
