# Rendering LEGO Bricks with Blender

Yes! You can absolutely render LEGO bricks using Blender. This guide shows you how to export your brick assemblies and render them with Blender's powerful rendering engine.

## Why Use Blender?

**Advantages of Blender rendering:**
- **Higher quality**: Advanced materials, lighting, and rendering engines (Cycles, Eevee)
- **More control**: Full control over camera, lighting, materials, and post-processing
- **Animation**: Create animations and turntables
- **Professional output**: Export to various formats (PNG, EXR, video)
- **Advanced features**: Depth of field, motion blur, compositing

**When to use:**
- High-quality renders for presentations/papers
- Creating animations or turntables
- When you need specific lighting or materials
- For final publication-quality images

## Quick Start

### 1. Export Your Assembly

```bash
# Inside container
docker exec -it lego_release-jeremy bash

# Export a single brick
python export_to_blender.py --brick_type 3001 --output brick_3001.obj

# Export custom assembly
python export_to_blender.py \
    --brick_types 3001 3001 3002 \
    --positions "0,0,0" "20,0,0" "10,0,8" \
    --output my_assembly.obj \
    --with_colors \
    --create_blender_script

# Export from JSON data
python export_to_blender.py \
    --json_path data/eval_datasets/synthetic_test/set_0/metadata.json \
    --output assembly.obj \
    --only_final \
    --create_blender_script
```

### 2. Import into Blender

**Option A: Using the generated script (easiest)**
1. Open Blender
2. Go to **Scripting** workspace
3. Open the generated `*_blender_import.py` script
4. Run it (Alt+P or click Run)

**Option B: Manual import**
1. Open Blender
2. File → Import → Wavefront (.obj)
3. Select your exported `.obj` file
4. Adjust import settings if needed

### 3. Render

1. Set up camera and lighting (or use the script's defaults)
2. Press **F12** to render
3. Or use **Render → Render Image**

---

## Export Script Usage

### Basic Export

```bash
# Single brick
python export_to_blender.py --brick_type 3001 --output brick.obj

# Custom assembly
python export_to_blender.py \
    --brick_types 3001 3001 3002 \
    --positions "0,0,0" "20,0,0" "10,0,8" \
    --output assembly.obj
```

### Export Options

**File formats:**
- `--output file.obj` - OBJ format (most compatible)
- `--output file.ply` - PLY format
- `--output file.stl` - STL format
- `--output file.glb` - GLTF/GLB format (modern, includes materials)

**Additional options:**
- `--with_colors` - Include vertex colors in export
- `--separate` - Export each brick as separate file
- `--only_final` - Only export final step (for JSON)
- `--create_blender_script` - Generate Blender import script

### Examples

**Export with colors:**
```bash
python export_to_blender.py \
    --brick_type 3001 \
    --output brick_colored.obj \
    --with_colors
```

**Export from evaluation data:**
```bash
python export_to_blender.py \
    --json_path data/eval_datasets/synthetic_test/set_0/metadata.json \
    --output eval_assembly.obj \
    --only_final \
    --with_colors \
    --create_blender_script
```

**Export each brick separately:**
```bash
python export_to_blender.py \
    --brick_types 3001 3001 3002 \
    --positions "0,0,0" "20,0,0" "10,0,8" \
    --output bricks \
    --separate
# Creates: bricks_000.obj, bricks_001.obj, bricks_002.obj
```

---

## Blender Workflow

### Step 1: Import the Mesh

**Using generated script:**
```python
# The script automatically:
# - Imports the mesh
# - Centers it
# - Adds lighting
# - Sets up camera
# - Configures render settings
```

**Manual import:**
1. File → Import → Wavefront (.obj)
2. Navigate to your exported file
3. Click "Import OBJ"

### Step 2: Set Up Materials

**Quick material setup:**
1. Select the imported mesh
2. Go to **Material Properties** tab
3. Click **New** to create material
4. Adjust:
   - **Base Color**: LEGO brick color (e.g., red: #E31837)
   - **Roughness**: 0.3-0.5 for plastic look
   - **Metallic**: 0.0 (LEGO bricks aren't metallic)
   - **Specular**: 0.5

**Using vertex colors (if exported with --with_colors):**
1. In Material Properties
2. Set **Base Color** to use **Vertex Color**
3. Colors from export will be used

### Step 3: Lighting Setup

**Basic three-point lighting:**
1. **Key light** (main): Sun or Area light, energy 3-5
2. **Fill light** (softer): Area light, energy 1-2
3. **Rim light** (back): Spot light, energy 2-3

**Quick setup:**
```python
# Add sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.object.data.energy = 3

# Add fill light
bpy.ops.object.light_add(type='AREA', location=(-5, -5, 8))
bpy.context.object.data.energy = 1.5
bpy.context.object.data.size = 5
```

### Step 4: Camera Setup

**Position camera:**
```python
# Add camera
bpy.ops.object.camera_add(location=(10, -10, 8))
bpy.context.object.rotation_euler = (1.1, 0, 0.785)  # 45° angle

# Set as active camera
bpy.context.scene.camera = bpy.context.object
```

**Or manually:**
1. Add → Camera
2. Position and rotate in 3D viewport
3. Press **Numpad 0** to view from camera
4. Adjust until satisfied

### Step 5: Render Settings

**For high quality:**
1. Go to **Render Properties**
2. Set **Render Engine**: Cycles or Eevee
3. **Samples**: 128-256 (Cycles) or 64 (Eevee)
4. **Resolution**: 1920x1920 or higher
5. **Output**: PNG with transparency

**Quick render:**
- Press **F12** to render
- Or **Render → Render Image**

---

## Advanced Blender Techniques

### Creating a Turntable Animation

```python
import bpy
import math

# Set animation length
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250  # 10 seconds at 25fps

# Get camera
camera = bpy.context.scene.camera

# Animate camera rotation
for frame in range(1, 251):
    angle = (frame / 250) * 2 * math.pi
    radius = 15
    camera.location = (
        radius * math.cos(angle),
        radius * math.sin(angle),
        8
    )
    camera.rotation_euler = (1.1, 0, angle + math.pi/4)
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)

# Render animation
bpy.ops.render.render(animation=True)
```

### Adding Depth of Field

1. Select camera
2. Camera Properties → Depth of Field
3. Enable **Depth of Field**
4. Set **Focus Object** to your mesh
5. Adjust **F-Stop** (lower = more blur)

### Using Cycles for Realistic Rendering

1. Render Properties → Render Engine: **Cycles**
2. **Device**: GPU Compute (if available)
3. **Samples**: 256-512 for final render
4. Add **World** environment texture for realistic lighting

### Material Presets

**Classic LEGO Red:**
- Base Color: #E31837
- Roughness: 0.3
- Specular: 0.5

**LEGO Yellow:**
- Base Color: #FFD700
- Roughness: 0.3
- Specular: 0.5

**LEGO Blue:**
- Base Color: #0055BF
- Roughness: 0.3
- Specular: 0.5

---

## Complete Example Workflow

### 1. Export from Python

```bash
python export_to_blender.py \
    --brick_types 3001 3001 3001 3002 \
    --positions "0,0,0" "20,0,0" "40,0,0" "20,0,8" \
    --output wall_assembly.obj \
    --with_colors \
    --create_blender_script
```

### 2. Open Blender and Run Script

1. Open Blender
2. Scripting workspace
3. Open `wall_assembly_blender_import.py`
4. Run script (Alt+P)

### 3. Enhance in Blender

1. **Materials**: Apply LEGO colors
2. **Lighting**: Adjust for best look
3. **Camera**: Fine-tune angle
4. **Render**: F12

### 4. Post-Processing (Optional)

1. Use Blender's **Compositor** for:
   - Color correction
   - Depth of field
   - Glow effects
   - Background replacement

---

## Comparison: PyTorch3D vs Blender

| Feature | PyTorch3D | Blender |
|---------|-----------|---------|
| **Speed** | Fast (GPU-accelerated) | Slower (but higher quality) |
| **Quality** | Good for quick previews | Excellent for final renders |
| **Materials** | Basic vertex colors | Advanced PBR materials |
| **Lighting** | Simple | Full control |
| **Animation** | Not supported | Full animation support |
| **Ease of use** | Simple Python API | Requires Blender knowledge |
| **Best for** | Quick visualization, debugging | Final renders, presentations |

**Recommendation:**
- Use **PyTorch3D** for quick previews and development
- Use **Blender** for final publication-quality renders

---

## Troubleshooting

### Mesh appears too small/large in Blender:
- Scale the mesh: Select → S → type scale factor
- Or adjust import scale in import dialog

### Colors not showing:
- Make sure you exported with `--with_colors`
- In Blender, set material to use Vertex Color

### Mesh appears at wrong position:
- The export script centers the mesh
- If needed, manually adjust position in Blender

### Import errors:
- Check file format matches extension
- Try different format (OBJ is most compatible)
- Ensure file path is correct

### Performance issues:
- Use Eevee instead of Cycles for faster renders
- Reduce sample count for preview renders
- Use GPU rendering if available

---

## Tips and Best Practices

1. **Export with colors** (`--with_colors`) for easier material setup
2. **Use OBJ format** for maximum compatibility
3. **Create Blender script** (`--create_blender_script`) for automated setup
4. **Start with simple lighting**, then enhance
5. **Use Cycles** for realistic materials, **Eevee** for speed
6. **Save your Blender file** (.blend) to preserve setup
7. **Use compositor** for post-processing effects

---

## Example: Complete Render Pipeline

```bash
# 1. Export assembly
python export_to_blender.py \
    --json_path data/eval_datasets/synthetic_test/set_0/metadata.json \
    --output final_assembly.obj \
    --only_final \
    --with_colors \
    --create_blender_script

# 2. In Blender:
#    - Open and run the generated script
#    - Adjust materials and lighting
#    - Render (F12)
#    - Save as PNG or EXR

# 3. Optional: Create animation
#    - Set up turntable (see example above)
#    - Render animation
#    - Export as video or image sequence
```

---

## Resources

- **Blender Documentation**: https://docs.blender.org/
- **Blender Python API**: https://docs.blender.org/api/current/
- **Trimesh Export Formats**: https://trimsh.org/trimesh.html#module-trimesh.exchange

Happy rendering! 🎨🧱

