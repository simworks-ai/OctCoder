import os
import glob
import subprocess
from typing import Dict, Any

def run_octave(script_path: str, run_dir: str, timeout: int = 300) -> Dict[str, Any]:
    """
    Execute a GNU Octave script by piping it to the CLI. This version
    intelligently selects the best available graphics toolkit to ensure
    stability and prevent crashes.

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
    os.makedirs(run_dir, exist_ok=True)

    try:
        with open(script_path, 'r') as f:
            user_script = f.read()

        # --- NEW ROBUST TOOLKIT SELECTION SCRIPT ---
        # This Octave code checks for available toolkits and picks the best one.
        # This prevents the "qt toolkit is not available" error.
        bootstrap_script = """
        % --- Smart Graphics Toolkit Selection ---
        available_toolkits = available_graphics_toolkits();
        if (ismember("qt", available_toolkits))
          graphics_toolkit("qt");
        elseif (ismember("fltk", available_toolkits))
          graphics_toolkit("fltk");
        else
          % Fallback to gnuplot if others are not available
          graphics_toolkit("gnuplot");
        end
        % Make it headless regardless of the toolkit
        set(0, 'DefaultFigureVisible', 'off');
        % --- End Smart Selection ---
        """
        
        full_script = bootstrap_script + user_script

        cmd = ["octave-cli", "--quiet"]

        proc = subprocess.run(
            cmd,
            input=full_script.encode(),
            cwd=run_dir,
            capture_output=True,
            timeout=timeout,
            check=False
        )
        
        stdout = proc.stdout.decode()
        stderr = proc.stderr.decode()

    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = f"TimeoutExpired: The Octave script ran for more than {timeout} seconds and was terminated."
    except FileNotFoundError:
        stdout = ""
        stderr = "Error: 'octave-cli' command not found. Please ensure GNU Octave is installed and in your system's PATH."

    # Discover generated frame PNGs
    pattern = os.path.join(run_dir, "frame_*.png")
    frames = sorted(glob.glob(pattern))

    return {"stdout": stdout, "stderr": stderr, "frames": frames}