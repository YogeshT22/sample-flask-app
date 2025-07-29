# Stage 1: Build stage
FROM python:3.9-slim-bookworm as builder

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# --- CONSOLIDATED INSTALLATION STEP ---
# This single RUN command ensures that caching works correctly.
# If requirements.txt changes, this whole layer gets re-run.
# We first upgrade pip and setuptools, then install from the requirements file.
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" && \
  pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim-bookworm

WORKDIR /app

# Copy only the installed Python packages from the builder stage.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
