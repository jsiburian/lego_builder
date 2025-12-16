#!/usr/bin/env python
"""
Interactive script for rendering and working with LEGO bricks.

This script provides an interactive Python environment for:
- Rendering single bricks or assemblies
- Creating custom brick arrangements
- Visualizing from JSON data
- Interactive exploration with matplotlib GUI

Usage:
    # Run interactively
    python interactive_bricks.py

    # Or import functions in your own scripts
    from interactive_bricks import render_interactive, create_custom_assembly
"""

import os
import sys
import json
from typing import List, Tuple, Optional

import matplotlib
import os
# Use TkAgg for GUI display (works with virtual desktop)
# If DISPLAY is not accessible, matplotlib will fail gracefully
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bricks.brick_info import Brick, BricksPC
from debug.utils import (
    visualize_brick,
    visualize_bricks,
    visualize_bricks_pc,
    load_bricks_pc,
    render_dict_simple,
    save_bricks_pc,
    save_bricks_pc_image,
    save_bricks_image
)


def render_interactive(image: Image.Image, title: str = "LEGO Bricks", block: bool = True):
    """
    Display a rendered image interactively using matplotlib.
    
    Args:
        image: PIL Image to display
        title: Window title
        block: If True, blocks until window is closed
    """
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis('off')
    plt.title(title, fontsize=16)
    plt.tight_layout()
    if block:
        plt.show()
    else:
        plt.draw()
        plt.pause(0.1)


def create_custom_assembly(
    brick_types: List[str],
    positions: List[Tuple[float, float, float]],
    rotations: List[Tuple[float, float, float, float]] = None,
    highlight: bool = False,
    show: bool = True,
    save_path: Optional[str] = None
) -> Image.Image:
    """
    Create and render a custom brick assembly.
    
    Args:
        brick_types: List of brick type strings (e.g., ["3001", "3002"])
        positions: List of (x, y, z) positions for each brick
        rotations: List of quaternion rotations (w, x, y, z). If None, uses default (1,0,0,0)
        highlight: Enable edge highlighting
        show: Display the image interactively
        save_path: Optional path to save the image
        
    Returns:
        PIL Image of the rendered assembly
    """
    if rotations is None:
        rotations = [(1, 0, 0, 0)] * len(brick_types)
    
    if len(rotations) != len(brick_types):
        rotations = [(1, 0, 0, 0)] * len(brick_types)
    
    bricks = []
    for i, (brick_type, pos, rot) in enumerate(zip(brick_types, positions, rotations)):
        bricks.append(Brick(brick_type, pos, rot))
        print(f"  Brick {i+1}: Type {brick_type}, Position {pos}, Rotation {rot}")
    
    print(f"\nRendering {len(bricks)} bricks...")
    image = visualize_bricks(bricks, highlight=highlight, adjust_camera=True)
    
    if save_path:
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)
            print(f"Saved to: {save_path}")
        except (OSError, IOError) as e:
            print(f"Warning: Could not save image to {save_path}: {e}")
            print("Continuing with display only...")
    
    if show:
        render_interactive(image, title=f"Custom Assembly ({len(bricks)} bricks)")
    
    return image


def explore_brick_types(brick_types: List[str] = None, highlight: bool = False):
    """
    Explore different brick types interactively.
    
    Args:
        brick_types: List of brick types to explore. If None, uses common examples
        highlight: Enable edge highlighting
    """
    if brick_types is None:
        # Common LEGO brick types
        brick_types = ["3001", "3002", "3003", "3004", "3005", "3010", "3020", "3021"]
    
    print(f"Exploring {len(brick_types)} brick types...")
    
    for i, brick_type in enumerate(brick_types):
        print(f"\n[{i+1}/{len(brick_types)}] Rendering brick type: {brick_type}")
        image = visualize_brick(brick_type, highlight=highlight, adjust_camera=True)
        render_interactive(image, title=f"Brick Type: {brick_type}", block=False)
        
        response = input("Press Enter for next brick, 'q' to quit, 's' to save: ").strip().lower()
        plt.close()
        
        if response == 'q':
            break
        elif response == 's':
            save_path = f"debug/brick_{brick_type}.png"
            os.makedirs("debug", exist_ok=True)
            image.save(save_path)
            print(f"Saved to: {save_path}")


def render_from_data_file(json_path: str, only_final: bool = False, show: bool = True):
    """
    Render bricks from a data dictionary JSON file.
    
    Args:
        json_path: Path to JSON file with brick data
        only_final: If True, only render the final step
        show: Display images interactively
    """
    print(f"Loading data from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print("Rendering assembly...")
    images = render_dict_simple(data, only_final=only_final, no_check=False)
    
    if only_final:
        images = [images]
    
    print(f"Rendered {len(images)} step(s)")
    
    for i, img in enumerate(images):
        title = f"Step {i+1}" if len(images) > 1 else "Final Assembly"
        if show:
            render_interactive(img, title=title, block=(i == len(images) - 1))
        else:
            save_path = f"debug/step_{i}.png"
            os.makedirs("debug", exist_ok=True)
            img.save(save_path)
            print(f"Saved to: {save_path}")


def interactive_menu():
    """Interactive menu for exploring LEGO bricks."""
    print("\n" + "="*60)
    print("LEGO Bricks Interactive Renderer")
    print("="*60)
    print("\nOptions:")
    print("1. Render a single brick type")
    print("2. Explore multiple brick types")
    print("3. Create custom assembly")
    print("4. Render from JSON data file")
    print("5. Render from saved BricksPC")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        brick_type = input("Enter brick type (e.g., 3001): ").strip()
        highlight = input("Enable highlighting? (y/n): ").strip().lower() == 'y'
        image = visualize_brick(brick_type, highlight=highlight, adjust_camera=True)
        render_interactive(image, title=f"Brick Type: {brick_type}")
        
        save = input("Save image? (y/n): ").strip().lower() == 'y'
        if save:
            save_path = f"debug/brick_{brick_type}.png"
            os.makedirs("debug", exist_ok=True)
            image.save(save_path)
            print(f"Saved to: {save_path}")
    
    elif choice == '2':
        highlight = input("Enable highlighting? (y/n): ").strip().lower() == 'y'
        explore_brick_types(highlight=highlight)
    
    elif choice == '3':
        print("\nCreate custom assembly:")
        print("Enter brick information (format: type x y z [w x y z for rotation])")
        print("Example: 3001 0 0 0")
        print("Example with rotation: 3001 0 0 0 1 0 0 0")
        print("Type 'done' when finished")
        
        brick_types = []
        positions = []
        rotations = []
        
        while True:
            line = input("Brick: ").strip()
            if line.lower() == 'done':
                break
            
            parts = line.split()
            if len(parts) < 4:
                print("Invalid format. Need at least: type x y z")
                continue
            
            brick_type = parts[0]
            pos = tuple(map(float, parts[1:4]))
            
            if len(parts) >= 8:
                rot = tuple(map(float, parts[4:8]))
            else:
                rot = (1, 0, 0, 0)  # Default rotation
            
            brick_types.append(brick_type)
            positions.append(pos)
            rotations.append(rot)
            print(f"  Added: {brick_type} at {pos} with rotation {rot}")
        
        if brick_types:
            highlight = input("Enable highlighting? (y/n): ").strip().lower() == 'y'
            create_custom_assembly(brick_types, positions, rotations, highlight=highlight)
        else:
            print("No bricks added.")
    
    elif choice == '4':
        json_path = input("Enter JSON file path: ").strip()
        if os.path.exists(json_path):
            only_final = input("Only render final step? (y/n): ").strip().lower() == 'y'
            render_from_data_file(json_path, only_final=only_final)
        else:
            print(f"File not found: {json_path}")
    
    elif choice == '5':
        bricks_pc_path = input("Enter BricksPC file path (or press Enter for default): ").strip()
        if not bricks_pc_path:
            bricks_pc_path = "debug/bs.json"
        
        if os.path.exists(bricks_pc_path):
            highlight = input("Enable highlighting? (y/n): ").strip().lower() == 'y'
            bricks_pc = load_bricks_pc(bricks_pc_path)
            image = visualize_bricks_pc(bricks_pc, highlight=highlight, adjust_camera=True)
            render_interactive(image, title="BricksPC Assembly")
            
            save = input("Save image? (y/n): ").strip().lower() == 'y'
            if save:
                save_path = f"debug/brickspc_rendered.png"
                os.makedirs("debug", exist_ok=True)
                image.save(save_path)
                print(f"Saved to: {save_path}")
        else:
            print(f"File not found: {bricks_pc_path}")
    
    elif choice == '6':
        print("Goodbye!")
        return False
    
    else:
        print("Invalid choice.")
    
    return True


def main():
    """Main entry point."""
    os.makedirs("debug", exist_ok=True)
    
    # Check if running in interactive mode or with command line args
    if len(sys.argv) > 1:
        # Command line mode
        import argparse
        parser = argparse.ArgumentParser(description='Interactive LEGO brick renderer')
        parser.add_argument('--brick_type', type=str, help='Single brick type to render')
        parser.add_argument('--json_path', type=str, help='Path to JSON data file')
        parser.add_argument('--bricks_pc_path', type=str, help='Path to BricksPC file')
        parser.add_argument('--highlight', action='store_true', help='Enable edge highlighting')
        parser.add_argument('--only_final', action='store_true', help='Only render final step')
        parser.add_argument('--no_show', action='store_true', help='Don\'t display GUI (save only)')
        
        args = parser.parse_args()
        
        if args.brick_type:
            image = visualize_brick(args.brick_type, highlight=args.highlight, adjust_camera=True)
            if not args.no_show:
                render_interactive(image, title=f"Brick Type: {args.brick_type}")
            save_path = f"debug/brick_{args.brick_type}.png"
            image.save(save_path)
            print(f"Saved to: {save_path}")
        
        elif args.json_path:
            render_from_data_file(args.json_path, only_final=args.only_final, show=not args.no_show)
        
        elif args.bricks_pc_path:
            bricks_pc = load_bricks_pc(args.bricks_pc_path)
            image = visualize_bricks_pc(bricks_pc, highlight=args.highlight, adjust_camera=True)
            if not args.no_show:
                render_interactive(image, title="BricksPC Assembly")
            save_path = "debug/brickspc_rendered.png"
            image.save(save_path)
            print(f"Saved to: {save_path}")
        
        else:
            print("No input specified. Use --help for usage.")
    else:
        # Interactive menu mode
        while True:
            try:
                if not interactive_menu():
                    break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")


if __name__ == '__main__':
    main()

