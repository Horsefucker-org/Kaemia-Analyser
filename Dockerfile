FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY safety_checker.py .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make it executable
RUN chmod +x safety_checker.py

# Default: interactive menu
ENTRYPOINT ["python3", "safety_checker.py"]
CMD ["--menu"]
