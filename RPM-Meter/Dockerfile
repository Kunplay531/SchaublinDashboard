
# Use the official Python 3 slim image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgpiod2 python3-libgpiod

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file to the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose any ports the application might use (optional, adjust as needed)
EXPOSE 8000

# Command to run the asyncio Python script
CMD ["python", "RPMMeter.py"]
