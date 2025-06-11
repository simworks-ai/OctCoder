

import os
import imageio
from typing import List

def make_gif(frame_paths: List[str], output_path: str, duration: float = 0.1) -> None:
    """
    Create an animated GIF from a list of image file paths, then delete the frames.

    Args:
        frame_paths: List of file paths to the PNG frames, in order.
        output_path: Path where the output GIF should be saved.
        duration: Time in seconds between frames in the GIF.
    """
    # Read all frames
    frames = []
    for fp in frame_paths:
        try:
            img = imageio.imread(fp)
            frames.append(img)
        except Exception as e:
            # Skip frames that can't be read
            continue

    if not frames:
        raise ValueError("No valid frames to compile into GIF.")

    # Write out the GIF
    imageio.mimsave(output_path, frames, format='GIF', duration=duration)

    # Cleanup PNG frames
    for fp in frame_paths:
        try:
            os.remove(fp)
        except OSError:
            pass