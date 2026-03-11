FROM ubuntu:24.04

# Prevent interactive prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies for PyGObject and PyInstaller
# We install python3-gi to get the precompiled system libraries for GTK4
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory where the repository will be mounted
WORKDIR /workspace

# Run the build.sh script when the container executes
CMD ["bash", "/workspace/build.sh"]
