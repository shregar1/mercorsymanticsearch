# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set environment variables to avoid interaction prompts
ENV DEBIAN_FRONTEND=noninteractive
# Set the time zone
ENV TZ=Asia/Kolkata

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    ntp \
    curl \
    wget \
    gcc \
    g++ \
    libsqlite3-dev \
    libpq-dev \
    software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA to install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set alternatives for python3 and pip3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Copy the requirements.txt first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the FastAPI application code to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Create a temporary directory for uploads, if needed
RUN mkdir -p /app/temp

# Set permissions for the temp directory
RUN chmod -R 777 /app/temp