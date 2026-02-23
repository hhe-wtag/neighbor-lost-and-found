# Use official Python image
FROM python:3.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first (for caching dependencies)
COPY pyproject.toml uv.lock ./

# Install pip and uvicorn
RUN pip install --upgrade pip \
    && pip install uvicorn \
    && pip install .

# Copy the rest of the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
