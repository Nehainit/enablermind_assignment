# Use official Python image with pre-built wheels
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-web.txt ./

# Install Python dependencies (skip tiktoken if it fails)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements-web.txt || \
    (pip install --no-deps crewai && \
     pip install openai duckduckgo-search requests beautifulsoup4 lxml \
     markdown weasyprint python-dotenv pydantic pydantic-settings \
     structlog pytest pytest-mock fastapi uvicorn jinja2 python-multipart aiofiles)

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
