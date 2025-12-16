# Virtual Desktop Usage Guide

This guide explains how to use the virtual desktop environment with your LEGO release project.

## Quick Start

### 1. Start the Services

```bash
# Start both desktop and lego_release containers
docker-compose up -d

# Check that both are running
docker-compose ps
```

### 2. Access the Virtual Desktop

1. **Open your web browser** and navigate to:
   ```
   http://localhost:6080
   ```

2. You should see a **noVNC web interface** with a desktop environment (typically XFCE or similar)

3. **Click "Connect"** or the connection should be automatic

4. You'll now see a **full desktop environment** in your browser!

## Using the Virtual Desktop

### Basic Desktop Operations

- **Mouse**: Click and drag as normal
- **Keyboard**: Type directly in the browser window
- **Right-click**: Works for context menus
- **Copy/Paste**: Use Ctrl+C and Ctrl+V (may need to use browser's copy/paste)

### Opening Applications

The virtual desktop comes with standard Linux applications:
- Terminal emulator
- File manager
- Text editors
- Web browser (within the desktop)

## Running GUI Applications from lego_release Container

Since both containers share the X11 display server, you can run GUI applications from your `lego_release-jeremy` container and they will appear in the virtual desktop.

### Example 1: Python Visualization (matplotlib)

```bash
# Enter the lego_release container
docker exec -it lego_release-jeremy bash

# Inside the container, run Python with GUI backend
python -c "
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Test Plot')
plt.show()
"
```

The plot window will appear in the virtual desktop at `http://localhost:6080`.

### Example 2: OpenCV Image Display

```bash
# Inside lego_release container
python -c "
import cv2
import numpy as np

# Create a test image
img = np.zeros((400, 400, 3), dtype=np.uint8)
cv2.rectangle(img, (100, 100), (300, 300), (0, 255, 0), 2)
cv2.putText(img, 'Hello from Container!', (50, 200), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

cv2.imshow('Test Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
"
```

### Example 3: Viewing Results/Images

```bash
# Inside lego_release container
# Open an image viewer
eog /workspace/results/some_image.png  # eog = Eye of GNOME image viewer

# Or use Python
python -c "
from PIL import Image
img = Image.open('/workspace/results/some_image.png')
img.show()
"
```

## Common Use Cases

### 1. Visualizing Training Results

```bash
# In lego_release container
python -c "
import matplotlib.pyplot as plt
# Your visualization code here
plt.figure(figsize=(10, 6))
# ... plot your data ...
plt.savefig('/workspace/results/plot.png')
plt.show()  # Will display in virtual desktop
"
```

### 2. Debugging with GUI Tools

```bash
# Open a file in a text editor within the desktop
# Or use command-line tools that open GUI windows
```

### 3. Interactive Data Exploration

```bash
# Run Jupyter notebook (if installed)
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Then access it via the desktop's browser at http://localhost:8888
```

## Troubleshooting

### Desktop Not Loading

1. **Check if desktop container is running:**
   ```bash
   docker ps | grep lego_desktop
   ```

2. **Check logs:**
   ```bash
   docker logs lego_desktop
   ```

3. **Restart the desktop service:**
   ```bash
   docker-compose restart desktop
   ```

### GUI Applications Not Showing

1. **Verify DISPLAY variable:**
   ```bash
   docker exec lego_release-jeremy echo $DISPLAY
   # Should output: :12
   ```

2. **Check X11 socket mount:**
   ```bash
   docker exec lego_release-jeremy ls -la /tmp/.X11-unix
   ```

3. **Test X11 connection:**
   ```bash
   docker exec lego_release-jeremy xeyes  # If xeyes is installed
   # Or
   docker exec lego_release-jeremy xclock
   ```

### Port Already in Use

If port 6080 is already in use, change it in `docker-compose.yml`:

```yaml
ports:
  - "6081:6080"  # Use 6081 instead
```

Then access at `http://localhost:6081`

## Advanced Usage

### Accessing Desktop Container Directly

```bash
# Enter the desktop container
docker exec -it lego_desktop bash

# You can install additional GUI applications here
apt-get update
apt-get install -y <package-name>
```

### Sharing Files Between Containers

Files in mounted volumes are automatically shared:
- `/workspace` in lego_release container
- Mounted directories are accessible from both containers

### Custom Display Number

If you need a different display number, update both containers in `docker-compose.yml`:

```yaml
environment:
  - DISPLAY=:13  # Change from :12 to :13
```

## Tips

1. **Full Screen**: Most browsers support F11 for fullscreen mode
2. **Scaling**: Adjust browser zoom if the desktop appears too small/large
3. **Performance**: For better performance, use a modern browser (Chrome, Firefox, Edge)
4. **Multiple Windows**: You can open multiple browser tabs with `http://localhost:6080` for different sessions
5. **Keyboard Shortcuts**: Some shortcuts may be captured by the browser - use the virtual desktop's keyboard settings if needed

## Stopping the Services

```bash
# Stop both services
docker-compose down

# Or stop just the desktop (lego_release will also stop due to depends_on)
docker-compose stop desktop
```

