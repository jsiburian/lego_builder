# Docker Setup

This repository includes Docker support for easy deployment and reproducibility.

## Prerequisites

- Docker installed on your system
- NVIDIA Docker runtime (nvidia-docker2) for GPU support
- CUDA 11.1 compatible GPU (for training/inference)

## Building the Docker Image

Build the Docker image using:

```bash
docker build -t lego_release:latest .
```

This will:
- Install all system dependencies
- Set up conda environment with Python 3.9.12
- Install PyTorch 1.8.0 with CUDA 11.1 support
- Install PyTorch3d 0.5.0 (built from source)
- Install all Python dependencies from requirements.txt

**Note:** Building PyTorch3d from source can take 10-20 minutes.

## Running with Docker

### Basic Usage

```bash
docker run --gpus all -it --rm \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/results:/workspace/results \
  lego_release:latest
```

### Using Docker Compose

The docker-compose.yml includes two services:

1. **desktop**: Virtual desktop environment (noVNC web interface)
2. **lego_release**: Main application container

Start both services:

```bash
docker-compose up -d
```

Access the virtual desktop:
- Open your browser and go to `http://localhost:6080`
- You'll see a web-based desktop environment

Access the application container:

```bash
docker-compose exec lego_release bash
```

Or directly by container name:

```bash
docker exec -it lego_release-jeremy bash
```

The desktop service provides a GUI environment that the lego_release container can use for visualization and GUI applications. Both services share the X11 display server.

## Running Evaluation

Once inside the container:

```bash
# Make sure you have downloaded the evaluation datasets and model checkpoints
bash scripts/eval/eval_all.sh
```

## Running Training

```bash
# Make sure you have downloaded the training datasets
bash scripts/process_dataset.sh
bash scripts/train/train_mepnet.sh
```

## Virtual Desktop Integration

The docker-compose setup includes a virtual desktop service that provides:
- Web-based GUI access via noVNC (port 6080)
- X11 display server for GUI applications
- Shared display between desktop and lego_release containers

This allows you to:
- Visualize results in a GUI environment
- Run visualization tools (matplotlib, OpenCV displays, etc.)
- Debug with GUI applications
- Access a full desktop environment in your browser

**Note:** The desktop service must be running before the lego_release service starts (enforced by `depends_on`).

## Notes

- The conda environment `lego_release` is automatically activated when you start a bash session
- Data directories should be mounted as volumes (see docker-compose.yml for examples)
- For multi-GPU training, adjust `CUDA_VISIBLE_DEVICES` in docker-compose.yml or use `--gpus all` with specific device IDs
- Both services share the X11 socket (`/tmp/.X11-unix`) for GUI support
- The DISPLAY environment variable is set to `:12` for both services

