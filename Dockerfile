# Stage 1: Build stage
FROM python:3.9-slim-bookworm as builder

WORKDIR /app

# Copy both requirements and our new constraints file
COPY requirements.txt .
COPY constraints.txt .

# --- CONSOLIDATED AND CACHE-BUSTED INSTALLATION ---
# By using the constraints file, we ensure pip installs the correct, secure versions.
# The -c flag tells pip to use the versions specified in this file.
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Stage 2: Final stage
FROM python:3.9-slim-bookworm

WORKDIR /app

# Copy only the installed Python packages from the builder stage.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
