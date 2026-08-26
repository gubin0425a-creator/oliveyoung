# Use official lightweight Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . /app/

# Expose port (Hugging Face Spaces routes traffic through this)
EXPOSE 8501

# Run Flask app
CMD ["python", "app.py"]
