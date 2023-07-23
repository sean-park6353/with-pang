# Base image
FROM python:3.8-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app to the container
COPY . .

# Expose the port that the Flask app will listen on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
