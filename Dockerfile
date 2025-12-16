# Use NVIDIA CUDA base image with Python (pip-based, no conda)
# Note: NVIDIA CUDA images require patch versions in tags
FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /workspace

# Install system dependencies and Python 3.9.12
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    x11-apps \
    x11-utils \
    x11-xserver-utils \
    software-properties-common \
    ninja-build \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python3.9-tk \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.9 (needed for some packages that uv might fall back to)
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py

# Create symlinks for python and pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3 1

# Install uv (fast Python package installer)
RUN pip install uv

# Verify uv is installed and available
RUN uv --version

# Install PyTorch 1.8.0 with CUDA 11.1 support via uv
# Note: uv pip install works like pip but faster, --system installs globally
RUN uv pip install --system torch==1.8.0+cu111 torchvision==0.9.0+cu111 --extra-index-url https://download.pytorch.org/whl/cu111

# Install PyTorch3d 0.5.0 dependencies
RUN uv pip install --system fvcore iopath

# Install build dependencies first (needed for packages like pycocotools)
# These need to be in the system Python before building packages that depend on them
RUN uv pip install --system cython numpy

# Copy requirements file
COPY requirements.txt /workspace/requirements.txt

# Install Python dependencies
# pycocotools 2.0.2 has broken source distribution - install from git instead
# The git version has the correct source file structure
# Use --no-build-isolation so it can use numpy/cython from system environment
RUN pip install --no-build-isolation 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

# Install remaining dependencies with uv, excluding pycocotools and pytorch3d (installed separately)
# Filter out pycocotools and pytorch3d from requirements.txt since they're installed from git
RUN grep -v "^pycocotools\|^pytorch3d" requirements.txt > /tmp/requirements_filtered.txt && \
    uv pip install --system -r /tmp/requirements_filtered.txt && \
    rm /tmp/requirements_filtered.txt

# Download and install CUB library (required for PyTorch3D CUDA compilation)
# CUB is a CUDA library for parallel primitives
# Using CUB 1.10.0 which is compatible with PyTorch3D 0.5.0 and CUDA 11.1
RUN cd /tmp && \
    wget https://github.com/NVIDIA/cub/archive/1.10.0.tar.gz && \
    tar -xzf 1.10.0.tar.gz && \
    mv cub-1.10.0 /opt/cub && \
    rm 1.10.0.tar.gz

# Install PyTorch3d 0.5.0 from source (after other dependencies are installed)
# Use --no-build-isolation so it can use torch from system environment
# Set FORCE_CUDA=1 to ensure CUDA support is enabled during build
# Set CUDA_HOME to help the build system find CUDA
# Set CUB_HOME to point to the CUB library
# Set TORCH_CUDA_ARCH_LIST to specify CUDA architectures (common ones for compatibility)
ENV FORCE_CUDA=1
ENV CUDA_HOME=/usr/local/cuda
ENV CUB_HOME=/opt/cub
ENV TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6"
RUN uv pip install --system --no-build-isolation 'git+https://github.com/facebookresearch/pytorch3d.git@v0.5.0'

# Copy the entire project
COPY . /workspace/

# Set environment variables
ENV PYTHONPATH=/workspace
ENV OMP_NUM_THREADS=1

# Default command
CMD ["/bin/bash"]
