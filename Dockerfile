FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and run the application using gunicorn with uvicorn worker and the custom configuration
EXPOSE 3100
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]