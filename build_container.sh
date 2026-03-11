#!/bin/bash
# Helper script to compile HIPAA Lockdown inside an Ubuntu 24.04 LTS Docker container
# for maximum glibc backwards compatibility.

set -e

echo "=========================================="
echo " Starting LTS Container Build Process     "
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed."
    echo "Please run: sudo apt-get install -y docker.io"
    exit 1
fi

echo "1. Building the Docker image (hipaa-lockdown-builder:24.04)..."
sudo docker build --network=host -t hipaa-lockdown-builder:24.04 .

echo "2. Running the build inside the container..."
# Mount the current directory strictly to /workspace inside the container
# The Dockerfile CMD will execute /workspace/build.sh automatically
sudo docker run --rm --network=host -v "$(pwd):/workspace" hipaa-lockdown-builder:24.04

echo "3. Fixing permissions and ownership of build artifacts..."
sudo chown -R $USER:$USER dist/
chmod +x dist/hipaa-lockdown-*

echo "=========================================="
echo " Containerized Build Complete!            "
echo " The LTS-compatible standalone executables"
echo " are now located in your ./dist directory."
echo "=========================================="
