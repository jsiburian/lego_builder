# How to Create a Custom LEGO Assembly

This guide shows you how to create your own custom LEGO brick assemblies.

## Method 1: Using the Interactive Script (Easiest)

### Step-by-Step:

1. **Start the interactive script:**
   ```bash
   docker exec -it lego_release-jeremy bash
   python interactive_bricks.py
   ```

2. **Select option 3:**
   ```
   Enter your choice (1-6): 3
   ```

3. **Enter brick information:**
   - Format: `brick_type x y z [rotation]`
   - Type `done` when finished
   - Each brick is added one at a time

4. **Example session:**
   ```
   Create custom assembly:
   Enter brick information (format: type x y z [w x y z for rotation])
   Example: 3001 0 0 0
   Example with rotation: 3001 0 0 0 1 0 0 0
   Type 'done' when finished

   Brick: 3001 0 0 0
     Added: 3001 at (0.0, 0.0, 0.0) with rotation (1, 0, 0, 0)
   
   Brick: 3001 20 0 0
     Added: 3001 at (20.0, 0.0, 0.0) with rotation (1, 0, 0, 0)
   
   Brick: 3002 10 0 8
     Added: 3002 at (10.0, 0.0, 8.0) with rotation (1, 0, 0, 0)
   
   Brick: done
   ```

5. **Choose highlighting:**
   ```
   Enable highlighting? (y/n): y
   ```

6. **View the result:**
   - The assembly renders in a GUI window
   - You can see all bricks together

---

## Method 2: Python Script (More Control)

### Basic Example:

```python
from interactive_bricks import create_custom_assembly

# Define your assembly
brick_types = ["3001", "3001", "3002"]
positions = [
    (0, 0, 0),      # First brick at origin
    (20, 0, 0),     # Second brick 20 units to the right
    (10, 0, 8)      # Third brick centered and 8 units up
]
rotations = [
    (1, 0, 0, 0),   # No rotation (identity quaternion)
    (1, 0, 0, 0),   # No rotation
    (1, 0, 0, 0)    # No rotation
]

# Create and render
image = create_custom_assembly(
    brick_types,
    positions,
    rotations,
    highlight=True,
    show=True,
    save_path="my_custom_assembly.png"
)
```

### Advanced Example with Rotations:

```python
from interactive_bricks import create_custom_assembly
import numpy as np
import trimesh.transformations as tr

# Create a rotated brick
# Rotate 90 degrees around Z-axis
rotation_90z = tr.quaternion_from_euler(0, 0, np.pi/2)

brick_types = ["3001", "3001", "3002"]
positions = [
    (0, 0, 0),
    (20, 0, 0),
    (10, 0, 8)
]
rotations = [
    (1, 0, 0, 0),           # No rotation
    tuple(rotation_90z),     # Rotated 90° around Z
    (1, 0, 0, 0)            # No rotation
]

image = create_custom_assembly(
    brick_types, positions, rotations,
    highlight=True, show=True
)
```

---

## Method 3: Direct Python API (Most Flexible)

### Using the Core Functions:

```python
from bricks.brick_info import Brick
from debug.utils import visualize_bricks, save_bricks_image

# Create brick objects
bricks = [
    Brick("3001", (0, 0, 0), (1, 0, 0, 0)),      # Brick at origin
    Brick("3001", (20, 0, 0), (1, 0, 0, 0)),     # Brick 20 units right
    Brick("3001", (40, 0, 0), (1, 0, 0, 0)),     # Brick 40 units right
    Brick("3002", (10, 0, 8), (1, 0, 0, 0)),     # Brick on top, centered
    Brick("3002", (30, 0, 8), (1, 0, 0, 0)),     # Another brick on top
]

# Render
image = visualize_bricks(bricks, highlight=True, adjust_camera=True)

# Save
image.save("my_assembly.png")

# Or display
import matplotlib.pyplot as plt
plt.imshow(image)
plt.axis('off')
plt.show()
```

---

## Understanding Coordinates

### LEGO Coordinate System:

- **X-axis**: Left/Right (horizontal)
- **Y-axis**: Forward/Back (depth)
- **Z-axis**: Up/Down (vertical, stacking)

### Standard LEGO Units:

- **Stud spacing**: 8 units (distance between stud centers)
- **Brick height**: 8 units (for standard bricks)
- **Plate height**: 3.2 units (for plates)

### Common Patterns:

**Side-by-side (horizontal):**
```python
Brick("3001", (0, 0, 0), (1, 0, 0, 0))    # First brick
Brick("3001", (20, 0, 0), (1, 0, 0, 0))   # 20 units to the right
Brick("3001", (40, 0, 0), (1, 0, 0, 0))   # 40 units to the right
```

**Stacked (vertical):**
```python
Brick("3001", (0, 0, 0), (1, 0, 0, 0))    # Bottom brick
Brick("3001", (0, 0, 8), (1, 0, 0, 0))    # 8 units up (on top)
Brick("3001", (0, 0, 16), (1, 0, 0, 0))  # 16 units up (two bricks high)
```

**Grid pattern:**
```python
# 2x2 grid
Brick("3001", (0, 0, 0), (1, 0, 0, 0))    # Bottom-left
Brick("3001", (20, 0, 0), (1, 0, 0, 0))   # Bottom-right
Brick("3001", (0, 0, 8), (1, 0, 0, 0))    # Top-left
Brick("3001", (20, 0, 8), (1, 0, 0, 0))   # Top-right
```

---

## Understanding Rotations

### Rotation Format: Quaternion (w, x, y, z)

- **(1, 0, 0, 0)**: No rotation (default)
- **Quaternion**: Represents 3D rotation

### Common Rotations:

**No rotation:**
```python
(1, 0, 0, 0)
```

**90° around Z-axis (rotate in XY plane):**
```python
(0.707, 0, 0, 0.707)  # or (0.707, 0, 0, -0.707)
```

**180° around Z-axis:**
```python
(0, 0, 0, 1)  # or (0, 0, 0, -1)
```

### Converting Euler Angles to Quaternion:

```python
import numpy as np
import trimesh.transformations as tr

# Rotate 90 degrees around Z-axis
rotation_90z = tr.quaternion_from_euler(0, 0, np.pi/2)
# Returns: (0.707, 0, 0, 0.707)

# Rotate 45 degrees around X-axis
rotation_45x = tr.quaternion_from_euler(np.pi/4, 0, 0)

# Rotate 30 degrees around Y-axis
rotation_30y = tr.quaternion_from_euler(0, np.pi/6, 0)
```

---

## Complete Examples

### Example 1: Simple Wall

```python
from interactive_bricks import create_custom_assembly

# Create a simple wall: 3 bricks side by side
brick_types = ["3001", "3001", "3001"]
positions = [
    (0, 0, 0),
    (20, 0, 0),
    (40, 0, 0)
]
rotations = [(1, 0, 0, 0)] * 3

create_custom_assembly(brick_types, positions, rotations, highlight=True)
```

### Example 2: Stacked Tower

```python
from interactive_bricks import create_custom_assembly

# Create a tower: 4 bricks stacked
brick_types = ["3001", "3001", "3001", "3001"]
positions = [
    (0, 0, 0),   # Bottom
    (0, 0, 8),   # Second level
    (0, 0, 16),  # Third level
    (0, 0, 24)   # Top
]
rotations = [(1, 0, 0, 0)] * 4

create_custom_assembly(brick_types, positions, rotations, highlight=True)
```

### Example 3: L-Shaped Structure

```python
from interactive_bricks import create_custom_assembly

# Create an L-shape
brick_types = ["3001", "3001", "3001", "3002"]
positions = [
    (0, 0, 0),    # Base left
    (20, 0, 0),   # Base center
    (40, 0, 0),   # Base right
    (40, 0, 8)    # Top right (vertical part of L)
]
rotations = [(1, 0, 0, 0)] * 4

create_custom_assembly(brick_types, positions, rotations, highlight=True)
```

### Example 4: Complex Assembly with Different Brick Types

```python
from interactive_bricks import create_custom_assembly

# Mix different brick types
brick_types = [
    "3001",  # 2x4 brick
    "3001",  # 2x4 brick
    "3002",  # 2x3 brick
    "3003",  # 2x2 brick
    "3004",  # 1x2 brick
]
positions = [
    (0, 0, 0),    # 2x4 at origin
    (20, 0, 0),   # 2x4 next to it
    (40, 0, 0),   # 2x3 further right
    (0, 0, 8),    # 2x2 on top of first
    (20, 0, 8),   # 1x2 on top of second
]
rotations = [(1, 0, 0, 0)] * 5

create_custom_assembly(
    brick_types, positions, rotations,
    highlight=True, show=True,
    save_path="complex_assembly.png"
)
```

### Example 5: Using Programmatic Generation

```python
from bricks.brick_info import Brick
from debug.utils import visualize_bricks

# Generate a grid programmatically
bricks = []
grid_size = 3  # 3x3 grid

for x in range(grid_size):
    for z in range(grid_size):
        pos = (x * 20, 0, z * 8)  # 20 units apart horizontally, 8 units vertically
        bricks.append(Brick("3001", pos, (1, 0, 0, 0)))

# Render
image = visualize_bricks(bricks, highlight=True, adjust_camera=True)
image.save("grid_assembly.png")
print(f"Created {len(bricks)}-brick grid assembly")
```

---

## Tips and Best Practices

### 1. Start Simple
- Begin with 2-3 bricks to test
- Verify positions look correct
- Then add more bricks

### 2. Use Standard Spacing
- Horizontal: Multiples of 20 (2x4 brick width)
- Vertical: Multiples of 8 (brick height)
- This ensures proper alignment

### 3. Test Positions
- Render frequently to check placement
- Use highlighting to see edges clearly
- Adjust camera if needed (automatic by default)

### 4. Save Your Work
```python
# Always save interesting assemblies
image.save("my_assembly.png")

# Or use the save function
save_bricks_image(bricks, highlight=True, name="my_assembly")
```

### 5. Common Brick Types Reference
- `3001`: 2x4 brick (most common)
- `3002`: 2x3 brick
- `3003`: 2x2 brick
- `3004`: 1x2 brick
- `3005`: 1x1 brick
- `3010`: 1x4 brick
- `3020`: 2x4 plate
- `3021`: 2x3 plate

---

## Troubleshooting

### Bricks appear too close or overlapping:
- Check your coordinates
- Use standard spacing (20 units horizontal, 8 units vertical)
- Render with highlighting to see edges

### Bricks appear in wrong positions:
- Verify coordinate order: (x, y, z)
- Check that rotations are correct
- Try simpler positions first

### Assembly looks wrong:
- Use `highlight=True` to see brick edges
- Check that brick types are valid
- Verify rotations are quaternions (4 values)

### Can't see the assembly:
- Camera auto-adjusts by default
- Try different brick positions
- Use `adjust_camera=True` (default)

---

## Next Steps

1. **Experiment**: Try different brick arrangements
2. **Save**: Keep interesting assemblies
3. **Combine**: Use saved assemblies in larger projects
4. **Share**: Export images to show your creations

Happy building! 🧱

