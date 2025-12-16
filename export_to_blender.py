#!/usr/bin/env python
"""
Export LEGO brick assemblies to Blender-compatible formats.

This script exports brick assemblies to OBJ, PLY, or STL files that can be
imported into Blender for advanced rendering, animation, and visualization.

Usage:
    # Export a single brick
    python export_to_blender.py --brick_type 3001 --output brick_3001.obj
    
    # Export custom assembly
    python export_to_blender.py --brick_types 3001 3001 3002 \
        --positions "0,0,0" "20,0,0" "10,0,8" \
        --output my_assembly.obj
    
    # Export from JSON data
    python export_to_blender.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json \
        --output assembly.obj
    
    # Export from BricksPC
    python export_to_blender.py --bricks_pc_path debug/bs.json --output assembly.obj
    
    # Export as separate files (one per brick)
    python export_to_blender.py --brick_type 3001 --output brick.obj --separate
    
    # Export with colors
    python export_to_blender.py --brick_type 3001 --output brick.obj --with_colors
"""

import argparse
import json
import os
import sys
from typing import List, Tuple, Optional

import numpy as np
import trimesh

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bricks.brick_info import Brick, BricksPC
from bricks.bricks import brick2mesh, get_brick_canonical_mesh
from debug.utils import load_bricks_pc


def export_brick_to_mesh(brick: Brick, color: Optional[Tuple[int, int, int]] = None) -> trimesh.Trimesh:
    """
    Convert a Brick object to a trimesh object.
    
    Args:
        brick: Brick object to convert
        color: Optional RGB color tuple (0-255)
        
    Returns:
        trimesh.Trimesh object
    """
    mesh = brick2mesh(brick, color=color)
    return mesh


def export_bricks_to_mesh(
    bricks: List[Brick],
    colors: Optional[List[Tuple[int, int, int]]] = None,
    merge: bool = True
) -> trimesh.Trimesh:
    """
    Convert a list of bricks to a trimesh object.
    
    Args:
        bricks: List of Brick objects
        colors: Optional list of RGB color tuples
        merge: If True, merge all bricks into single mesh. If False, return list.
        
    Returns:
        trimesh.Trimesh or list of trimesh.Trimesh objects
    """
    meshes = []
    
    for i, brick in enumerate(bricks):
        color = colors[i] if colors and i < len(colors) else None
        mesh = export_brick_to_mesh(brick, color)
        meshes.append(mesh)
    
    if merge:
        # Combine all meshes into one
        combined = trimesh.util.concatenate(meshes)
        return combined
    else:
        return meshes


def export_bricks_pc_to_mesh(
    bricks_pc: BricksPC,
    colors: Optional[List[Tuple[int, int, int]]] = None,
    merge: bool = True
) -> trimesh.Trimesh:
    """
    Convert a BricksPC object to a trimesh object.
    
    Args:
        bricks_pc: BricksPC object
        colors: Optional list of RGB color tuples
        merge: If True, merge all bricks into single mesh
        
    Returns:
        trimesh.Trimesh or list of trimesh.Trimesh objects
    """
    from debug.utils import get_elements
    
    bricks = get_elements(bricks_pc.bricks)
    return export_bricks_to_mesh(bricks, colors, merge)


def export_to_file(
    mesh: trimesh.Trimesh,
    output_path: str,
    format: Optional[str] = None
):
    """
    Export a mesh to a file.
    
    Args:
        mesh: trimesh.Trimesh object
        output_path: Output file path
        format: File format ('obj', 'ply', 'stl', 'glb'). If None, inferred from extension.
    """
    if format is None:
        format = os.path.splitext(output_path)[1][1:].lower()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Export based on format
    if format == 'obj':
        mesh.export(output_path, file_type='obj')
    elif format == 'ply':
        mesh.export(output_path, file_type='ply')
    elif format == 'stl':
        mesh.export(output_path, file_type='stl')
    elif format == 'glb' or format == 'gltf':
        mesh.export(output_path, file_type='glb')
    else:
        # Try to export with trimesh's auto-detection
        mesh.export(output_path)
    
    print(f"Exported to: {output_path}")
    print(f"  Format: {format}")
    print(f"  Vertices: {len(mesh.vertices)}")
    print(f"  Faces: {len(mesh.faces)}")


def export_from_json(
    json_path: str,
    output_path: str,
    only_final: bool = False,
    with_colors: bool = True
):
    """
    Export bricks from a JSON data file.
    
    Args:
        json_path: Path to JSON metadata file
        output_path: Output file path
        only_final: If True, only export final step
        with_colors: If True, use colors from JSON
    """
    print(f"Loading data from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    bricks = []
    colors = []
    
    # Collect all bricks from operations
    for i_str, op in data['operations'].items():
        if only_final and int(i_str) != len(data['operations']) - 1:
            continue
        
        b_step = op['bricks']
        for j in range(len(b_step)):
            rotation = b_step[j]['brick_transform']['rotation']
            position = b_step[j]['brick_transform']['position']
            
            if 'brick_type' in b_step[j]:
                brick_type = b_step[j]['brick_type']
                brick = Brick(brick_type, position, rotation)
                bricks.append(brick)
                
                if with_colors and 'color' in b_step[j]:
                    colors.append(tuple(b_step[j]['color']))
                else:
                    colors.append(None)
            else:
                # Handle CBrick (composite brick)
                from bricks.brick_info import dict_to_cbrick
                cbrick = dict_to_cbrick(b_step[j], no_check=False)
                # Expand CBrick into individual bricks
                for sub_brick in cbrick.bricks:
                    bricks.append(sub_brick)
                    if with_colors and 'color' in b_step[j]:
                        colors.append(tuple(b_step[j]['color']))
                    else:
                        colors.append(None)
    
    print(f"Found {len(bricks)} bricks")
    
    # Export
    mesh = export_bricks_to_mesh(bricks, colors if with_colors else None, merge=True)
    export_to_file(mesh, output_path)


def create_blender_import_script(output_path: str, mesh_path: str):
    """
    Create a Blender Python script to import and render the mesh.
    
    Args:
        output_path: Path to save the Blender script
        mesh_path: Path to the exported mesh file
    """
    script_content = f'''"""
Blender script to import and render LEGO brick assembly.

Usage in Blender:
    1. Open Blender
    2. Go to Scripting workspace
    3. Open this script
    4. Run the script (Alt+P or click Run)
    
Or run from command line:
    blender --background --python {os.path.basename(output_path)}
"""

import bpy
import os

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import the mesh
mesh_path = r"{mesh_path}"
file_format = os.path.splitext(mesh_path)[1][1:].lower()

if file_format == 'obj':
    bpy.ops.import_scene.obj(filepath=mesh_path)
elif file_format == 'ply':
    bpy.ops.import_mesh.ply(filepath=mesh_path)
elif file_format == 'stl':
    bpy.ops.import_mesh.stl(filepath=mesh_path)
elif file_format in ['glb', 'gltf']:
    bpy.ops.import_scene.gltf(filepath=mesh_path)
else:
    print(f"Unsupported format: {{file_format}}")
    print("Supported formats: obj, ply, stl, glb, gltf")

# Select all imported objects
bpy.ops.object.select_all(action='SELECT')

# Center the model
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
bpy.ops.object.location_clear()

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.object.data.energy = 3

# Add camera
bpy.ops.object.camera_add(location=(10, -10, 8))
bpy.context.object.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = bpy.context.object

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1920
bpy.context.scene.render.image_settings.file_format = 'PNG'

print("Mesh imported successfully!")
print("You can now:")
print("  - Adjust materials and lighting")
print("  - Render the scene (F12)")
print("  - Export as other formats")
'''
    
    with open(output_path, 'w') as f:
        f.write(script_content)
    
    print(f"Created Blender import script: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Export LEGO brick assemblies to Blender-compatible formats')
    parser.add_argument('--brick_type', type=str, help='Single brick type to export')
    parser.add_argument('--brick_types', nargs='+', help='Multiple brick types')
    parser.add_argument('--positions', nargs='+', help='Positions as "x,y,z" strings')
    parser.add_argument('--rotations', nargs='+', help='Rotations as quaternions "w,x,y,z" (optional)')
    parser.add_argument('--json_path', type=str, help='Path to JSON data file')
    parser.add_argument('--bricks_pc_path', type=str, help='Path to BricksPC file')
    parser.add_argument('--output', type=str, required=True, help='Output file path')
    parser.add_argument('--format', type=str, choices=['obj', 'ply', 'stl', 'glb'], help='File format (auto-detected from extension if not specified)')
    parser.add_argument('--separate', action='store_true', help='Export each brick as separate file')
    parser.add_argument('--with_colors', action='store_true', help='Include colors in export')
    parser.add_argument('--only_final', action='store_true', help='Only export final step (for JSON)')
    parser.add_argument('--create_blender_script', action='store_true', help='Create Blender Python script for import')
    
    args = parser.parse_args()
    
    # Determine output format
    format_ext = os.path.splitext(args.output)[1][1:].lower() if args.output else None
    output_format = args.format or format_ext or 'obj'
    
    # Ensure output has correct extension
    if not args.output.endswith(f'.{output_format}'):
        args.output = f"{args.output}.{output_format}"
    
    mesh = None
    meshes = None
    
    if args.brick_type:
        # Single brick
        brick = Brick(args.brick_type, (0, 0, 0), (1, 0, 0, 0))
        mesh = export_brick_to_mesh(brick, color=(255, 0, 0) if args.with_colors else None)
        
    elif args.brick_types:
        # Custom assembly
        if not args.positions:
            print("Error: --positions required when using --brick_types")
            sys.exit(1)
        
        bricks = []
        colors = []
        
        for i, brick_type in enumerate(args.brick_types):
            if i >= len(args.positions):
                print(f"Warning: Not enough positions for brick {i+1}, skipping")
                break
            
            pos_str = args.positions[i]
            pos = tuple(map(float, pos_str.split(',')))
            
            if args.rotations and i < len(args.rotations):
                rot_str = args.rotations[i]
                rot = tuple(map(float, rot_str.split(',')))
            else:
                rot = (1, 0, 0, 0)
            
            brick = Brick(brick_type, pos, rot)
            bricks.append(brick)
            
            if args.with_colors:
                # Use different colors for different bricks
                import random
                colors.append((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
        
        if args.separate:
            meshes = export_bricks_to_mesh(bricks, colors if args.with_colors else None, merge=False)
        else:
            mesh = export_bricks_to_mesh(bricks, colors if args.with_colors else None, merge=True)
    
    elif args.json_path:
        # Export from JSON
        export_from_json(args.json_path, args.output, args.only_final, args.with_colors)
        mesh = None  # Already exported
    
    elif args.bricks_pc_path:
        # Export from BricksPC
        bricks_pc = load_bricks_pc(args.bricks_pc_path)
        if args.separate:
            meshes = export_bricks_pc_to_mesh(bricks_pc, merge=False)
        else:
            mesh = export_bricks_pc_to_mesh(bricks_pc, merge=True)
    
    else:
        print("Error: Must specify one of: --brick_type, --brick_types, --json_path, or --bricks_pc_path")
        sys.exit(1)
    
    # Export mesh(es)
    if meshes is not None:
        # Export separate files
        base_name = os.path.splitext(args.output)[0]
        ext = os.path.splitext(args.output)[1]
        for i, m in enumerate(meshes):
            output_file = f"{base_name}_{i:03d}{ext}"
            export_to_file(m, output_file, output_format)
        print(f"\nExported {len(meshes)} separate files")
    elif mesh is not None:
        # Export single file
        export_to_file(mesh, args.output, output_format)
    
    # Create Blender script if requested
    if args.create_blender_script:
        script_path = os.path.splitext(args.output)[0] + '_blender_import.py'
        create_blender_import_script(script_path, args.output)
        print(f"\nTo use in Blender:")
        print(f"  1. Open Blender")
        print(f"  2. Go to Scripting workspace")
        print(f"  3. Open: {script_path}")
        print(f"  4. Run the script")


if __name__ == '__main__':
    main()

