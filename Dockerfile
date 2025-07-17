FROM python:3.9-slim

WORKDIR /app

# Copy requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/system_status || exit 1

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV FLASK_APP=web_app.py

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web_app:app"]