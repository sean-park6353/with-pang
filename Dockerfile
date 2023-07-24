# Base image
FROM python:3.8-alpine

RUN apk add --no-cache gcc musl-dev && apk add --no-cache libffi-dev && apk add --no-cache bash

WORKDIR /app

COPY requirements.txt .

COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Run the Flask app
CMD ["python3", "app.py"]
