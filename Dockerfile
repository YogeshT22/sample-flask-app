# Stage 1: Build stage - Use a modern, secure base image
# We are sticking with bookworm as it's the current stable Debian release.
FROM python:3.9-slim-bookworm as builder

WORKDIR /app

# Copy requirements first to leverage Docker's layer cache
COPY requirements.txt .

# --- SECURITY REMEDIATION STEP ---
# Upgrade pip and setuptools to specific, non-vulnerable versions BEFORE installing other requirements.
# This fixes the HIGH vulnerability CVE-2022-40897 found in the older setuptools.
RUN pip install --no-cache-dir --upgrade pip "setuptools==78.1.1"

# Now install the application's dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Final stage - Use the same secure base image
FROM python:3.9-slim-bookworm

WORKDIR /app

# Copy only the installed Python packages from the builder stage.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
