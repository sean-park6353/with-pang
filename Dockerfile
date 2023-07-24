# Base image
FROM python:3.8-alpine

RUN apk add --no-cache gcc musl-dev
RUN apk add --no-cache libffi-dev

# Set the working directory in the container
WORKDIR /app

# Install bash for the wait-for-it.sh script
RUN apk add --no-cache bash

# Copy the requirements file to the container
COPY requirements.txt .

# Copy the Flask app to the container
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt


# Expose the port that the Flask app will listen on
EXPOSE 443

# Run the Flask app
CMD ["python3", "app.py"]
