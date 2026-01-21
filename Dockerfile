FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including VNC and X11
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    xvfb \
    x11vnc \
    xterm \
    fluxbox \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Create directory for VNC
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

USER app

# Expose ports
EXPOSE 8000
# VNC ports range (5900-5999)
EXPOSE 5900-5999

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["python", "-m", "computer_use_backend.main"]