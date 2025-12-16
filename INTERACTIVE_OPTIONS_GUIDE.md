# Interactive Bricks Script - Options Guide

This guide explains each option in the `interactive_bricks.py` script and how to use them.

## Running the Script

```bash
# Interactive menu mode
python interactive_bricks.py

# Command-line mode (see examples below)
python interactive_bricks.py --brick_type 3001
```

---

## Menu Options

When you run `python interactive_bricks.py` without arguments, you'll see this menu:

```
============================================================
LEGO Bricks Interactive Renderer
============================================================

Options:
1. Render a single brick type
2. Explore multiple brick types
3. Create custom assembly
4. Render from JSON data file
5. Render from saved BricksPC
6. Exit

Enter your choice (1-6):
```

---

## Option 1: Render a Single Brick Type

### What it does:
Renders one specific LEGO brick type in 3D. Useful for:
- Viewing what a specific brick looks like
- Testing rendering functionality
- Quick visualization

### How to use:
1. Select option `1`
2. Enter a brick type (e.g., `3001`, `3002`, `3003`)
3. Choose whether to enable highlighting (y/n)
4. The brick will render and display in a GUI window
5. Optionally save the image

### Example:
```
Enter your choice (1-6): 1
Enter brick type (e.g., 3001): 3001
Enable highlighting? (y/n): y
[Image displays in GUI window]
Save image? (y/n): y
Saved to: debug/brick_3001.png
```

### Command-line equivalent:
```bash
python interactive_bricks.py --brick_type 3001 --highlight
```

### Common brick types:
- `3001`: Standard 2x4 brick
- `3002`: Standard 2x3 brick
- `3003`: Standard 2x2 brick
- `3004`: Standard 1x2 brick
- `3005`: Standard 1x1 brick
- `3010`: Standard 1x4 brick
- `3020`: Standard 2x4 plate
- `3021`: Standard 2x3 plate

---

## Option 2: Explore Multiple Brick Types

### What it does:
Cycles through multiple brick types one by one, allowing you to:
- Compare different brick shapes
- Browse through a collection
- Save individual bricks as you go

### How to use:
1. Select option `2`
2. Choose whether to enable highlighting (y/n)
3. The script will show 8 common brick types by default
4. For each brick:
   - Press **Enter** to see the next brick
   - Type **'q'** to quit early
   - Type **'s'** to save the current brick

### Example:
```
Enter your choice (1-6): 2
Enable highlighting? (y/n): n

Exploring 8 brick types...

[1/8] Rendering brick type: 3001
[Image displays]
Press Enter for next brick, 'q' to quit, 's' to save: [Enter]

[2/8] Rendering brick type: 3002
[Image displays]
Press Enter for next brick, 'q' to quit, 's' to save: s
Saved to: debug/brick_3002.png
Press Enter for next brick, 'q' to quit, 's' to save: [Enter]
...
```

### What happens:
- Shows each brick in sequence
- You control the pace (press Enter to continue)
- Can save interesting bricks on the fly
- Can quit early if you've seen enough

---

## Option 3: Create Custom Assembly

### What it does:
Lets you build a custom LEGO assembly by specifying:
- Brick types
- Positions (x, y, z coordinates)
- Rotations (quaternion: w, x, y, z)

### How to use:
1. Select option `3`
2. Enter brick information one at a time
3. Format: `brick_type x y z [w x y z]`
4. Type `done` when finished
5. Choose highlighting option
6. The complete assembly renders

### Input format:
```
brick_type x y z [w x y z]
```

Where:
- `brick_type`: Brick type string (e.g., "3001")
- `x y z`: Position coordinates (floats)
- `w x y z`: Rotation quaternion (optional, defaults to 1 0 0 0)

### Examples:

**Simple example (no rotation):**
```
Brick: 3001 0 0 0
Brick: 3001 20 0 0
Brick: 3002 10 0 8
Brick: done
```

**With rotation:**
```
Brick: 3001 0 0 0 1 0 0 0
Brick: 3001 20 0 0 0.707 0 0.707 0
Brick: done
```

### Complete example session:
```
Enter your choice (1-6): 3

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

Rendering 3 bricks...
  Brick 1: Type 3001, Position (0.0, 0.0, 0.0), Rotation (1, 0, 0, 0)
  Brick 2: Type 3001, Position (20.0, 0.0, 0.0), Rotation (1, 0, 0, 0)
  Brick 3: Type 3002, Position (10.0, 0.0, 8.0), Rotation (1, 0, 0, 0)

Enable highlighting? (y/n): y
[Assembly renders in GUI window]
```

### Tips:
- **Coordinates**: LEGO units are typically in increments of 8 (stud spacing)
- **Position**: (0, 0, 0) is the origin
- **Rotation**: (1, 0, 0, 0) is no rotation (identity quaternion)
- **Stacking**: Increase z-coordinate to stack bricks vertically
- **Spacing**: Use x/y coordinates to place bricks side-by-side

### Command-line equivalent:
```python
from interactive_bricks import create_custom_assembly

brick_types = ["3001", "3001", "3002"]
positions = [(0, 0, 0), (20, 0, 0), (10, 0, 8)]
rotations = [(1, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0)]

create_custom_assembly(brick_types, positions, rotations, highlight=True)
```

---

## Option 4: Render from JSON Data File

### What it does:
Renders bricks from evaluation dataset JSON files. These files contain:
- Complete LEGO assembly instructions
- Step-by-step construction data
- Camera parameters
- Brick positions and rotations for each step

### How to use:
1. Select option `4`
2. Enter the path to a JSON metadata file
3. Choose whether to render only the final step or all steps
4. Images render and display

### Example paths:
```
data/eval_datasets/synthetic_test/set_0/metadata.json
data/eval_datasets/classics/set_0/metadata.json
data/eval_datasets/architecture/set_0/metadata.json
```

### Example session:
```
Enter your choice (1-6): 4
Enter JSON file path: data/eval_datasets/synthetic_test/set_0/metadata.json
Only render final step? (y/n): n

Loading data from: data/eval_datasets/synthetic_test/set_0/metadata.json
Rendering assembly...
Rendered 5 step(s)
[Step 1 image displays]
[Step 2 image displays]
...
[Step 5 image displays]
```

### What you'll see:
- **All steps**: Shows the assembly being built step-by-step
- **Final step only**: Shows just the completed assembly

### Command-line equivalent:
```bash
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json --only_final
```

### JSON file structure:
The JSON files contain:
- `operations`: Dictionary of construction steps
- Each step has `bricks` with positions, rotations, and types
- Camera parameters for each view
- Object scale and center for proper rendering

---

## Option 5: Render from Saved BricksPC

### What it does:
Loads and renders a previously saved BricksPC object. BricksPC is the internal data structure used to represent LEGO assemblies.

### How to use:
1. Select option `5`
2. Enter path to BricksPC file (or press Enter for default: `debug/bs.json`)
3. Choose highlighting option
4. The assembly renders

### Example session:
```
Enter your choice (1-6): 5
Enter BricksPC file path (or press Enter for default): debug/bs.json
Enable highlighting? (y/n): y
[Assembly renders in GUI window]
Save image? (y/n): y
Saved to: debug/brickspc_rendered.png
```

### When to use:
- After running evaluation scripts (they save BricksPC files)
- After creating assemblies programmatically
- To re-render previously saved assemblies

### Command-line equivalent:
```bash
python interactive_bricks.py --bricks_pc_path debug/bs.json --highlight
```

### File formats:
- `.json`: Human-readable JSON format
- `.pkl`: Python pickle format (binary)

---

## Option 6: Exit

Simply exits the program.

---

## Command-Line Mode

You can also use the script from the command line without the interactive menu:

### Render single brick:
```bash
python interactive_bricks.py --brick_type 3001
python interactive_bricks.py --brick_type 3001 --highlight
python interactive_bricks.py --brick_type 3001 --no_show  # Save only, no GUI
```

### Render from JSON:
```bash
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json --only_final
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json --no_show
```

### Render from BricksPC:
```bash
python interactive_bricks.py --bricks_pc_path debug/bs.json
python interactive_bricks.py --bricks_pc_path debug/bs.json --highlight
```

### All options:
- `--brick_type`: Single brick type to render
- `--json_path`: Path to JSON data file
- `--bricks_pc_path`: Path to BricksPC file
- `--highlight`: Enable edge highlighting
- `--only_final`: Only render final step (for JSON)
- `--no_show`: Don't display GUI, save only

---

## Common Workflows

### Workflow 1: Explore Available Bricks
```
1. Run: python interactive_bricks.py
2. Choose option 2 (Explore multiple brick types)
3. Browse through bricks, save interesting ones
```

### Workflow 2: Create a Simple Assembly
```
1. Run: python interactive_bricks.py
2. Choose option 3 (Create custom assembly)
3. Enter bricks one by one:
   - 3001 0 0 0
   - 3001 20 0 0
   - 3002 10 0 8
   - done
4. Enable highlighting
5. View and save result
```

### Workflow 3: Visualize Evaluation Data
```
1. Run: python interactive_bricks.py
2. Choose option 4 (Render from JSON)
3. Enter path: data/eval_datasets/synthetic_test/set_0/metadata.json
4. Choose to see all steps or final only
5. Review the rendered assembly
```

### Workflow 4: Quick Command-Line Rendering
```bash
# Quick render and save
python interactive_bricks.py --brick_type 3001 --no_show

# Render evaluation data
python interactive_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json --only_final --no_show
```

---

## Tips and Tricks

1. **Highlighting**: Use `--highlight` to see brick edges more clearly
2. **Virtual Desktop**: GUI windows appear at `http://localhost:6080`
3. **Saving**: Images are automatically saved to `debug/` directory
4. **Coordinates**: LEGO units use 8-unit spacing (stud-to-stud distance)
5. **Rotations**: Quaternion format (w, x, y, z), where (1, 0, 0, 0) = no rotation
6. **Batch Mode**: Use `--no_show` for automated rendering without GUI

---

## Troubleshooting

### GUI not showing:
- Make sure virtual desktop is running: `docker-compose ps`
- Check DISPLAY variable: `echo $DISPLAY` (should be `:12`)
- Try: `python -c "import matplotlib; matplotlib.use('TkAgg'); import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.show()"`

### File not found:
- Check file paths are relative to `/workspace` in container
- Use absolute paths if needed
- Verify files exist: `ls -la data/eval_datasets/...`

### Invalid brick type:
- Use valid LEGO brick type codes (e.g., "3001", "3002")
- Check available types in the codebase

---

Happy building! 🧱

