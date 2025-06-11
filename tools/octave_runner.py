import os
import glob
import subprocess
from typing import Dict, Any

def run_octave(script_path: str, run_dir: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute a GNU Octave script in CLI mode, capture stdout/stderr,
    and collect generated PNG frames from the specified run directory.

    Args:
        script_path: Path to the .m script to run.
        run_dir: Directory where frame_*.png files will be saved.
        timeout: Maximum seconds to wait for Octave to complete.

    Returns:
        A dict containing:
          - 'stdout': decoded standard output text.
          - 'stderr': decoded error output text.
          - 'frames': list of paths to frame PNG files, sorted by name.
    """
    # Ensure run_dir exists
    os.makedirs(run_dir, exist_ok=True)

    # --- FIX STARTS HERE ---
    # The script_path is a full path (e.g., 'test_runs/run1/script.m')
    # and run_dir is the directory ('test_runs/run1').
    # Since we set cwd=run_dir, the command only needs the script's filename.
    script_filename = os.path.basename(script_path)

    # Build the Octave CLI command.
    cmd = [
        "octave-cli",
        "--quiet",
        script_filename  # Use just the filename, not the full path
    ]
    # --- FIX ENDS HERE ---

    # Launch the process
    proc = subprocess.Popen(
        cmd,
        cwd=run_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, # Decode stdout/stderr as text using default encoding
    )
    try:
        # The process will wait here until the user closes the plot window (ending the 'pause;')
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stderr = f"TimeoutExpired: The Octave script ran for more than {timeout} seconds and was terminated.\n" + stderr

    # Discover generated frame PNGs
    pattern = os.path.join(run_dir, "frame_*.png")
    frames = sorted(glob.glob(pattern))

    return {"stdout": stdout, "stderr": stderr, "frames": frames}