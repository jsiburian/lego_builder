#!/usr/bin/env python
"""
Script to render LEGO bricks in 3D.

Usage examples:
    # Render a single brick type
    python render_bricks.py --brick_type 3001
    
    # Render from a data dictionary (JSON file)
    python render_bricks.py --json_path data/eval_datasets/synthetic_test/set_0/metadata.json
    
    # Render from BricksPC (saved brick assembly)
    python render_bricks.py --bricks_pc_path debug/bs.json
    
    # Render with highlighting
    python render_bricks.py --brick_type 3001 --highlight
    
    # Save to file
    python render_bricks.py --brick_type 3001 --output output.png
"""

import argparse
import json
import os
import sys

from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bricks.brick_info import Brick
from debug.utils import (
    visualize_brick,
    visualize_bricks,
    visualize_bricks_pc,
    load_bricks_pc,
    render_dict_simple,
    save_bricks_pc_image
)


def render_single_brick(brick_type, highlight=False, output=None):
    """Render a single brick by type."""
    print(f"Rendering brick type: {brick_type}")
    image = visualize_brick(brick_type, highlight=highlight, adjust_camera=True)
    
    if output:
        image.save(output)
        print(f"Saved to: {output}")
    else:
        output = f"debug/brick_{brick_type}.png"
        os.makedirs("debug", exist_ok=True)
        image.save(output)
        print(f"Saved to: {output}")
    
    return image


def render_from_json(json_path, only_final=False, output=None):
    """Render bricks from a data dictionary JSON file."""
    print(f"Loading data from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print("Rendering assembly...")
    images = render_dict_simple(data, only_final=only_final, no_check=False)
    
    if only_final:
        images = [images]
    
    if output:
        if len(images) == 1:
            images[0].save(output)
            print(f"Saved to: {output}")
        else:
            base_name = os.path.splitext(output)[0]
            ext = os.path.splitext(output)[1]
            for i, img in enumerate(images):
                img.save(f"{base_name}_step_{i}{ext}")
            print(f"Saved {len(images)} images to: {base_name}_step_*{ext}")
    else:
        os.makedirs("debug", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        for i, img in enumerate(images):
            output_path = f"debug/{base_name}_step_{i}.png"
            img.save(output_path)
            print(f"Saved to: {output_path}")
    
    return images


def render_from_bricks_pc(bricks_pc_path, highlight=False, output=None):
    """Render from a saved BricksPC object."""
    print(f"Loading BricksPC from: {bricks_pc_path}")
    bricks_pc = load_bricks_pc(bricks_pc_path)
    
    print("Rendering assembly...")
    image = visualize_bricks_pc(bricks_pc, highlight=highlight, adjust_camera=True)
    
    if output:
        image.save(output)
        print(f"Saved to: {output}")
    else:
        base_name = os.path.splitext(os.path.basename(bricks_pc_path))[0]
        output = f"debug/{base_name}_rendered.png"
        os.makedirs("debug", exist_ok=True)
        image.save(output)
        print(f"Saved to: {output}")
    
    return image


def render_custom_bricks(brick_types, positions, rotations, highlight=False, output=None):
    """Render custom bricks with specified types, positions, and rotations."""
    print(f"Rendering {len(brick_types)} custom bricks...")
    
    bricks = []
    for i, (brick_type, pos, rot) in enumerate(zip(brick_types, positions, rotations)):
        bricks.append(Brick(brick_type, pos, rot))
        print(f"  Brick {i+1}: Type {brick_type}, Position {pos}, Rotation {rot}")
    
    image = visualize_bricks(bricks, highlight=highlight, adjust_camera=True)
    
    if output:
        image.save(output)
        print(f"Saved to: {output}")
    else:
        output = "debug/custom_bricks.png"
        os.makedirs("debug", exist_ok=True)
        image.save(output)
        print(f"Saved to: {output}")
    
    return image


def main():
    parser = argparse.ArgumentParser(description='Render LEGO bricks in 3D')
    parser.add_argument('--brick_type', type=str, help='Single brick type to render (e.g., "3001")')
    parser.add_argument('--json_path', type=str, help='Path to JSON file with brick data dictionary')
    parser.add_argument('--bricks_pc_path', type=str, help='Path to saved BricksPC JSON/PKL file')
    parser.add_argument('--output', type=str, help='Output image path')
    parser.add_argument('--highlight', action='store_true', help='Enable edge highlighting')
    parser.add_argument('--only_final', action='store_true', help='Only render final step (for JSON)')
    parser.add_argument('--show', action='store_true', help='Display image in GUI (requires virtual desktop)')
    
    args = parser.parse_args()
    
    # Create debug directory if it doesn't exist
    os.makedirs("debug", exist_ok=True)
    
    if args.brick_type:
        image = render_single_brick(args.brick_type, highlight=args.highlight, output=args.output)
    elif args.json_path:
        if not os.path.exists(args.json_path):
            print(f"Error: File not found: {args.json_path}")
            sys.exit(1)
        images = render_from_json(args.json_path, only_final=args.only_final, output=args.output)
        image = images[0] if isinstance(images, list) else images
    elif args.bricks_pc_path:
        if not os.path.exists(args.bricks_pc_path):
            print(f"Error: File not found: {args.bricks_pc_path}")
            sys.exit(1)
        image = render_from_bricks_pc(args.bricks_pc_path, highlight=args.highlight, output=args.output)
    else:
        # Example: render a simple brick
        print("No input specified. Rendering example brick (type 3001)...")
        image = render_single_brick("3001", highlight=args.highlight, output=args.output)
    
    if args.show:
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            plt.imshow(image)
            plt.axis('off')
            plt.title('Rendered LEGO Bricks')
            plt.show()
            print("Image displayed in GUI window")
        except Exception as e:
            print(f"Could not display image: {e}")
            print("Image saved to file instead")
    
    print("Done!")


if __name__ == '__main__':
    main()

