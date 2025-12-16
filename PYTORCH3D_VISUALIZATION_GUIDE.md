# PyTorch3D Visualization and GUI Options

**Important:** PyTorch3D itself **does not have a built-in GUI**. It's a library for 3D deep learning that renders to images/tensors. However, there are several ways to visualize PyTorch3D outputs, which this guide covers.

## Overview

PyTorch3D renders 3D scenes to **images** (numpy arrays or PIL Images), not interactive 3D viewers. You then use other tools to display these images.

## Current Visualization Methods in This Codebase

### 1. **Matplotlib** (Primary Method)

**What it is:** Python plotting library with GUI support

**How it's used:**
```python
import matplotlib
matplotlib.use('TkAgg')  # GUI backend
import matplotlib.pyplot as plt
from PIL import Image

# PyTorch3D renders to PIL Image
image = visualize_bricks(bricks, highlight=True)

# Display with matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(image)
plt.axis('off')
plt.title('LEGO Bricks')
plt.show()  # Opens GUI window
```

**Features:**
- ✅ Simple and widely available
- ✅ Works with virtual desktop (X11 forwarding)
- ✅ Good for static images
- ❌ Not interactive 3D (just displays rendered images)
- ❌ Limited interactivity

**Backends:**
- `TkAgg`: Works with virtual desktop (used in this codebase)
- `Qt5Agg`: More features, requires Qt
- `Agg`: No GUI (for saving only)

**Usage in this codebase:**
- `interactive_bricks.py` - Uses matplotlib for GUI display
- `render_bricks.py` - Optional matplotlib display with `--show`
- `debug/utils.py` - Returns PIL Images (can be displayed with matplotlib)

### 2. **OpenCV** (cv2.imshow)

**What it is:** Computer vision library with simple image display

**How it's used:**
```python
import cv2
import numpy as np
from PIL import Image

# PyTorch3D renders to PIL Image
image = visualize_bricks(bricks)

# Convert and display
img_array = np.array(image)
cv2.imshow('LEGO Bricks', img_array)
cv2.waitKey(0)  # Wait for key press
cv2.destroyAllWindows()
```

**Features:**
- ✅ Very simple
- ✅ Fast display
- ✅ Good for quick previews
- ❌ Basic (no zoom, pan, etc.)
- ❌ Requires X11/GUI environment

**Usage in this codebase:**
- Mentioned in `VIRTUAL_DESKTOP_GUIDE.md`
- Not currently used in main scripts

### 3. **Visdom** (For Training)

**What it is:** Web-based visualization tool for training

**How it's used:**
```python
import visdom

vis = visdom.Visdom(server='http://localhost', port=8097)

# During training
vis.images(rendered_images, win='bricks', opts=dict(title='LEGO Bricks'))
```

**Features:**
- ✅ Web-based (access from browser)
- ✅ Good for monitoring training
- ✅ Can show multiple images
- ❌ Requires separate server
- ❌ More setup required

**Usage in this codebase:**
- `util/visualizer.py` - Visdom integration for training
- `options/train_options.py` - Training options include visdom settings
- Not used for interactive brick rendering

### 4. **Weights & Biases (wandb)** (For Experiments)

**What it is:** Experiment tracking and visualization

**How it's used:**
```python
import wandb

wandb.init(project='lego')

# Log rendered images
wandb.log({
    'brick_renders': [wandb.Image(img) for img in images]
})
```

**Features:**
- ✅ Cloud-based (or local)
- ✅ Great for experiment tracking
- ✅ Can compare multiple runs
- ❌ Requires account/setup
- ❌ Not for interactive use

**Usage in this codebase:**
- `train_kp.py` - Optional wandb logging
- `options/base_options.py` - `--wandb` flag
- Not used for interactive rendering

### 5. **Jupyter Notebooks**

**What it is:** Interactive Python notebooks with inline display

**How it's used:**
```python
from IPython.display import display
from PIL import Image

# Render with PyTorch3D
image = visualize_bricks(bricks)

# Display inline
display(image)
```

**Features:**
- ✅ Interactive development
- ✅ Inline display
- ✅ Can combine code and output
- ❌ Requires Jupyter server
- ❌ Not a true 3D viewer

**Usage in this codebase:**
- Not currently set up, but can be added

### 6. **Export to Blender** (For Advanced Rendering)

**What it is:** Export meshes and render in Blender

**How it's used:**
```bash
# Export mesh
python export_to_blender.py --brick_type 3001 --output brick.obj

# Import and render in Blender
# (See BLENDER_RENDERING_GUIDE.md)
```

**Features:**
- ✅ Professional quality rendering
- ✅ Full 3D control
- ✅ Animation support
- ❌ Requires Blender
- ❌ Not real-time

**Usage in this codebase:**
- `export_to_blender.py` - Export script
- `BLENDER_RENDERING_GUIDE.md` - Complete guide

---

## Comparison Table

| Method | Type | Interactivity | Setup | Best For |
|--------|------|--------------|-------|----------|
| **Matplotlib** | GUI Window | Low (static images) | Easy | Quick previews, development |
| **OpenCV** | GUI Window | Low (basic) | Easy | Quick checks |
| **Visdom** | Web Browser | Medium (web UI) | Medium | Training monitoring |
| **Wandb** | Web Browser | Medium (dashboards) | Medium | Experiment tracking |
| **Jupyter** | Browser | Medium (notebook) | Medium | Interactive development |
| **Blender** | Desktop App | High (full 3D) | Hard | Final renders, animations |

---

## What PyTorch3D Actually Does

PyTorch3D **renders 3D scenes to 2D images**, not interactive 3D viewers:

```python
# PyTorch3D rendering pipeline
mesh = join_meshes_as_scene(brick_meshes)  # 3D mesh
cameras = FoVOrthographicCameras(...)     # Camera setup
image, depth_map = render_lego_scene(mesh, cameras)  # Render to image
# Returns: PIL Image or numpy array (2D image)
```

**Key point:** PyTorch3D produces **static images**, not interactive 3D scenes.

---

## Interactive 3D Visualization Options

If you want **true interactive 3D** (rotate, zoom, pan), you need different tools:

### Option 1: **PyVista** (Python 3D Visualization)

```python
import pyvista as pv
import numpy as np

# Convert PyTorch3D mesh to PyVista
# (would need conversion function)
plotter = pv.Plotter()
plotter.add_mesh(mesh_pv)
plotter.show()  # Interactive 3D viewer
```

### Option 2: **Open3D** (3D Data Processing)

```python
import open3d as o3d

# Convert mesh to Open3D format
mesh_o3d = o3d.geometry.TriangleMesh()
# ... convert vertices/faces ...

o3d.visualization.draw_geometries([mesh_o3d])  # Interactive viewer
```

### Option 3: **Plotly** (Web-based 3D)

```python
import plotly.graph_objects as go

# Create 3D mesh plot
fig = go.Figure(data=[go.Mesh3d(...)])
fig.show()  # Interactive web-based 3D viewer
```

### Option 4: **Blender** (Full 3D Software)

- Import exported meshes
- Full 3D interaction
- Professional rendering

---

## Current Setup in This Codebase

### Primary Method: Matplotlib + Virtual Desktop

**How it works:**
1. PyTorch3D renders to PIL Image
2. Matplotlib displays the image in a GUI window
3. Virtual desktop (noVNC) shows the window in browser

**Example:**
```bash
# Start containers
docker-compose up -d

# Access virtual desktop
# Open browser: http://localhost:6080

# Inside container
docker exec -it lego_release-jeremy bash
python interactive_bricks.py --brick_type 3001
# Image appears in virtual desktop browser window
```

**Code location:**
- `interactive_bricks.py` - Main interactive script
- `render_bricks.py` - Command-line rendering with `--show` option
- Uses `matplotlib.use('TkAgg')` for GUI backend

---

## Creating Your Own Visualization

### Simple Image Display

```python
from debug.utils import visualize_bricks
from bricks.brick_info import Brick
import matplotlib.pyplot as plt

# Render
bricks = [Brick("3001", (0, 0, 0), (1, 0, 0, 0))]
image = visualize_bricks(bricks)

# Display
plt.imshow(image)
plt.axis('off')
plt.show()
```

### Save to File (No GUI)

```python
image = visualize_bricks(bricks)
image.save("output.png")
```

### Custom Display Function

```python
def display_with_info(image, title="LEGO Bricks", info=None):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image)
    ax.axis('off')
    ax.set_title(title, fontsize=16)
    if info:
        ax.text(10, 10, info, fontsize=12, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    plt.tight_layout()
    plt.show()

# Use it
display_with_info(image, "My Assembly", "3 bricks, 2x4 type")
```

---

## Summary

**PyTorch3D doesn't have a GUI** - it renders 3D to 2D images. To visualize:

1. **For quick previews:** Use matplotlib (current setup)
2. **For training:** Use visdom or wandb
3. **For interactive 3D:** Use PyVista, Open3D, or Plotly
4. **For final renders:** Export to Blender

**Current codebase uses:** Matplotlib + Virtual Desktop for GUI display

**To see it in action:**
```bash
docker exec -it lego_release-jeremy bash
python interactive_bricks.py
# Choose option 1-5, images appear in virtual desktop
```

---

## FAQ

**Q: Can I rotate/zoom the 3D model interactively?**  
A: Not directly with PyTorch3D. You'd need to re-render from different camera angles, or use PyVista/Open3D/Blender.

**Q: Why not use a 3D viewer?**  
A: PyTorch3D is optimized for batch rendering and deep learning, not interactive visualization.

**Q: Can I make it interactive?**  
A: Yes, by re-rendering from different camera angles based on user input, or exporting to a 3D viewer.

**Q: What's the best for development?**  
A: Matplotlib (current setup) is good for quick previews. For true 3D interaction, consider PyVista.

---

For more details, see:
- `INTERACTIVE_RENDERING_GUIDE.md` - How to use current visualization
- `BLENDER_RENDERING_GUIDE.md` - Advanced rendering with Blender
- `VIRTUAL_DESKTOP_GUIDE.md` - Setting up GUI display

