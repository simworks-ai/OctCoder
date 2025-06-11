import os
import imageio
from typing import List
from PIL import Image
import numpy as np

def make_gif(frame_paths: List[str], output_path: str, duration: float = 0.1) -> None:
    """
    Create an animated GIF from a list of image file paths, then delete the frames.

    Args:
        frame_paths: List of file paths to the PNG frames, in order.
        output_path: Path where the output GIF should be saved.
        duration: Time in seconds between frames in the GIF.
    """
    frames = []
    max_width = 0
    max_height = 0
    
    # Read all frames and find max dimensions
    for fp in frame_paths:
        try:
            img = imageio.imread(fp)
            frames.append(img)
            h, w = img.shape[0], img.shape[1]
            max_height = max(max_height, h)
            max_width = max(max_width, w)
        except Exception as e:
            # Skip frames that can't be read or are invalid
            continue

    if not frames:
        raise ValueError("No valid frames to compile into GIF.")

    # Pad frames to a consistent size
    padded_frames = []
    for img_np in frames:
        # Convert numpy array to PIL Image
        if img_np.shape[2] == 4: # Check for RGBA
            img_pil = Image.fromarray(img_np, 'RGBA')
        else: # Assume RGB
            img_pil = Image.fromarray(img_np, 'RGB')
            
        # Create a new blank image with max dimensions (black background)
        # Use RGBA if any frame is RGBA, otherwise RGB
        new_img_pil = Image.new(img_pil.mode, (max_width, max_height), (0, 0, 0, 0) if img_pil.mode == 'RGBA' else (0, 0, 0))
        
        # Paste the original image onto the new blank image
        new_img_pil.paste(img_pil, (0, 0))
        
        # Convert back to numpy array
        padded_frames.append(np.array(new_img_pil))

    # Write out the GIF
    imageio.mimsave(output_path, padded_frames, format='GIF', duration=duration)

    # Cleanup PNG frames
    for fp in frame_paths:
        try:
            os.remove(fp)
        except OSError:
            pass