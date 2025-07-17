FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY notebooks/ ./notebooks/

# Set environment variables
ENV PYTHONPATH=/app
ENV MATPLOTLIB_BACKEND=Agg

# Expose port (if needed for web interface)
EXPOSE 8080

# Default command
CMD ["python", "scripts/main.py", "--stock", "RELIANCE.NS"]