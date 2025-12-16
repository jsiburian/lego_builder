# Interactive LEGO Brick Rendering Guide

This guide explains how to render and interactively work with LEGO bricks in 3D using PyTorch3D.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Command-Line Rendering](#command-line-rendering)
3. [Interactive Python Script](#interactive-python-script)
4. [Using the Virtual Desktop](#using-the-virtual-desktop)
5. [Python API Examples](#python-api-examples)
6. [Advanced Usage](#advanced-usage)

---

## Quick Start

### 1. Start the Docker containers

```bash
docker-compose up -d
```

### 2. Access the container

```bash
docker exec -it lego_release-jeremy bash
```

### 3. Test rendering

```bash
# Render a simple brick
python render_bricks.py --brick_type 3001 --show

# Or use the interactive script
python interactive_bricks.py
```

---

## Command-Line Rendering

### Basic Commands

The `render_bricks.py` script provides simple command-line rendering:

```bash
# Render a single brick type
python render_bricks.py --brick_type 3001

# Render with edge highlighting
python render_bricks.py --brick_type 3001 --highlight

# Save to specific file
python render_bricks.py --brick_type 3001 --output results/my_brick.png

# Display in GUI (requires virtual desktop)
python render_bricks.py --brick_type 3001 --show
```

### Render from Data Files

```bash
# Render from JSON metadata file
python render_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json

# Only render final step
python render_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json --only_final

# Render from saved BricksPC
python render_bricks.py --bricks_pc_path debug/bs.json --highlight
```

---

## Interactive Python Script

The `interactive_bricks.py` script provides a menu-driven interface for exploring bricks:

### Run Interactive Menu

```bash
python interactive_bricks.py
```

This will show a menu with options:
1. Render a single brick type
2. Explore multiple brick types
3. Create custom assembly
4. Render from JSON data file
5. Render from saved BricksPC
6. Exit

### Command-Line Mode

You can also use it from command line:

```bash
# Render single brick
python interactive_bricks.py --brick_type 3001

# Render from JSON
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json

# Render without GUI (save only)
python interactive_bricks.py --brick_type 3001 --no_show
```

---

## Using the Virtual Desktop

### Access the Virtual Desktop

1. **Start containers:**
   ```bash
   docker-compose up -d
   ```

2. **Open browser:** Navigate to `http://localhost:6080`

3. **You'll see a desktop environment** where GUI applications will appear

### Display Rendered Images

```bash
# Inside the container
docker exec -it lego_release-jeremy bash

# Render and display
python render_bricks.py --brick_type 3001 --show

# Or use interactive script
python interactive_bricks.py --brick_type 3001
```

The image window will appear in the virtual desktop at `http://localhost:6080`.

---

## Python API Examples

### Example 1: Render a Single Brick

```python
from debug.utils import visualize_brick
from PIL import Image

# Render brick type 3001
image = visualize_brick("3001", highlight=False, adjust_camera=True)

# Save to file
image.save("brick_3001.png")

# Display (if using virtual desktop)
import matplotlib.pyplot as plt
plt.imshow(image)
plt.axis('off')
plt.show()
```

### Example 2: Create Custom Assembly

```python
from bricks.brick_info import Brick
from debug.utils import visualize_bricks

# Create multiple bricks
bricks = [
    Brick("3001", (0, 0, 0), (1, 0, 0, 0)),      # Brick at origin
    Brick("3001", (20, 0, 0), (1, 0, 0, 0)),      # Brick 20 units to the right
    Brick("3002", (0, 0, 8), (1, 0, 0, 0)),       # Different brick type on top
]

# Render the assembly
image = visualize_bricks(bricks, highlight=True, adjust_camera=True)
image.save("custom_assembly.png")
```

### Example 3: Render from JSON Data

```python
import json
from debug.utils import render_dict_simple

# Load JSON file
with open("data/eval_datasets/synthetic_test/set_0/metadata.json", 'r') as f:
    data = json.load(f)

# Render all steps
images = render_dict_simple(data, only_final=False, no_check=False)

# Save each step
for i, img in enumerate(images):
    img.save(f"step_{i}.png")
```

### Example 4: Interactive Exploration

```python
from interactive_bricks import create_custom_assembly, explore_brick_types

# Explore different brick types
explore_brick_types(brick_types=["3001", "3002", "3003"], highlight=True)

# Create a custom assembly
brick_types = ["3001", "3001", "3002"]
positions = [(0, 0, 0), (20, 0, 0), (10, 0, 8)]
rotations = [(1, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0)]

image = create_custom_assembly(
    brick_types, 
    positions, 
    rotations, 
    highlight=True, 
    show=True,
    save_path="my_assembly.png"
)
```

### Example 5: Work with BricksPC

```python
from debug.utils import load_bricks_pc, visualize_bricks_pc, save_bricks_pc

# Load a saved BricksPC
bricks_pc = load_bricks_pc("debug/bs.json")

# Render it
image = visualize_bricks_pc(bricks_pc, highlight=True, adjust_camera=True)
image.save("brickspc_rendered.png")

# You can also save a BricksPC
# (assuming you have a BricksPC object)
# save_bricks_pc(bricks_pc, name="my_assembly")
```

---

## Advanced Usage

### Custom Camera Angles

You can modify camera parameters in `debug/utils.py` or create your own rendering function:

```python
from pytorch3d.renderer import look_at_view_transform, FoVOrthographicCameras
from debug.utils import bricks2meshes, render_lego_scene
from pytorch3d.structures import join_meshes_as_scene
import torch

bricks = [Brick("3001", (0, 0, 0), (1, 0, 0, 0))]
brick_meshes = bricks2meshes(bricks, [(255, 0, 0)])
mesh = join_meshes_as_scene(brick_meshes)

# Custom camera: elevation=45°, azimuth=180°
R, T = look_at_view_transform(dist=2000, elev=45, azim=180, at=((0, 0, 0),))
cameras = FoVOrthographicCameras(device='cuda', R=R, T=T, scale_xyz=[[0.0024, 0.0024, 0.0024]])

image, depth_map = render_lego_scene(mesh, cameras)
```

### Batch Rendering

```python
from debug.utils import visualize_brick
from PIL import Image

brick_types = ["3001", "3002", "3003", "3004", "3005"]
images = []

for brick_type in brick_types:
    img = visualize_brick(brick_type, highlight=False, adjust_camera=True)
    images.append(img)
    img.save(f"debug/brick_{brick_type}.png")

print(f"Rendered {len(images)} bricks")
```

### Animation (Multiple Views)

```python
import matplotlib.pyplot as plt
from debug.utils import visualize_brick
import numpy as np

brick_type = "3001"
azimuths = np.linspace(0, 360, 36)  # 36 views around the brick

for i, azim in enumerate(azimuths):
    # Note: You'd need to modify visualize_brick to accept camera parameters
    # This is a conceptual example
    img = visualize_brick(brick_type, highlight=False, adjust_camera=True)
    img.save(f"debug/rotation_{i:03d}.png")

print("Created 36-frame rotation animation")
```

---

## Common Brick Types

Here are some common LEGO brick types you can use:

- `3001`: Standard 2x4 brick
- `3002`: Standard 2x3 brick
- `3003`: Standard 2x2 brick
- `3004`: Standard 1x2 brick
- `3005`: Standard 1x1 brick
- `3010`: Standard 1x4 brick
- `3020`: Standard 2x4 plate
- `3021`: Standard 2x3 plate

---

## Troubleshooting

### GUI Not Showing

If images don't appear in the virtual desktop:

1. **Check virtual desktop is running:**
   ```bash
   docker-compose ps
   ```

2. **Verify DISPLAY variable:**
   ```bash
   docker exec -it lego_release-jeremy bash
   echo $DISPLAY  # Should show :12
   ```

3. **Test with simple matplotlib:**
   ```bash
   python -c "import matplotlib; matplotlib.use('TkAgg'); import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.show()"
   ```

### GPU Not Available

If rendering is slow, check GPU:

```bash
# Inside container
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Memory Issues

If you get out-of-memory errors:

- Reduce number of bricks in assembly
- Use `adjust_camera=False` to skip camera adjustment
- Render smaller images (modify resize in `debug/utils.py`)

---

## Tips

1. **Use highlighting** (`--highlight`) to see brick edges more clearly
2. **Save frequently** when experimenting with custom assemblies
3. **Use the interactive script** for exploration, command-line for automation
4. **Check `debug/` directory** for saved images and BricksPC files
5. **Virtual desktop** is great for interactive exploration, but not needed for batch rendering

---

## Next Steps

- Explore the evaluation datasets: `data/eval_datasets/`
- Check out `debug/utils.py` for more rendering functions
- Look at `data_generation/utils.py` for mesh generation utilities
- Read the paper for understanding the full pipeline

Happy building! 🧱

