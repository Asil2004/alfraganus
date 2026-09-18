# ==========================================
# Alfraganus AI Server - Docker Container
# ==========================================

FROM python:3.11-slim

# Install system dependencies for audio, vision and network tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libasound2-dev \
    portaudio19-dev \
    curl \
    iputils-ping \
    net-tools \
    android-tools-adb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose FastAPI & Web Dashboard port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run FastAPI Server Gateway
CMD ["python", "server/server_app.py"]
