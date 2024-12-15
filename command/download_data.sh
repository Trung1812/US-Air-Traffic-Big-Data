#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Define variables
FILENAME="airline_2m.tar.gz"
URL_PREFIX="https://dax-cdn.cdn.appdomain.cloud/dax-airline/1.0.1"
URL="${URL_PREFIX}/${FILENAME}"

# Define the local path to save the file
LOCAL_PREFIX="data/raw/airline"
LOCAL_PATH="${LOCAL_PREFIX}/${FILENAME}"

# Create the directory if it doesn't exist
echo "Creating directory ${LOCAL_PREFIX}..."
mkdir -p ${LOCAL_PREFIX}

# Download the file
echo "Downloading ${URL} to ${LOCAL_PATH}..."
wget ${URL} -O ${LOCAL_PATH}

# Print success message
echo "Download complete: ${LOCAL_PATH}"