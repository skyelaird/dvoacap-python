# DVOACAP Dashboard - Docker Container
# Easy deployment for HF propagation prediction dashboard

FROM python:3.11-slim

LABEL org.opencontainers.image.title="DVOACAP Dashboard"
LABEL org.opencontainers.image.description="HF Radio Propagation Prediction Dashboard"
LABEL org.opencontainers.image.authors="Skye Laird <skyelaird@users.noreply.github.com>"
LABEL org.opencontainers.image.source="https://github.com/skyelaird/dvoacap-python"
LABEL org.opencontainers.image.license="MIT"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire repository (needed for DVoaData and source code)
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dashboard]"

# Change to Dashboard directory
WORKDIR /app/Dashboard

# Environment variables for configuration
ENV CALLSIGN=NOCALL
ENV LAT=40.0
ENV LON=-75.0
ENV GRID=FN20
ENV ANTENNA="Vertical Monopole"
ENV PORT=8000

# Expose Flask server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/status')" || exit 1

# Run the Flask server
CMD ["python", "server.py"]
