# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies (Flask for now)
RUN pip install --no-cache-dir flask

# Expose port
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
