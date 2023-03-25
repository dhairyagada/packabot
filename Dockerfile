# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script and .env file into the container
COPY packabot2.py .env /app/

# Run the bot script
CMD ["python", "packabot2.py"]