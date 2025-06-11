

import os
import uuid
from dotenv import load_dotenv
from tools.octave_runner import run_octave
from tools.gif_utils import make_gif

# Load environment variables (e.g., GNUTERM, if needed)
load_dotenv()

def executor_agent(state: dict) -> dict:
    """
    Execution Agent: runs a GNU Octave .m script and returns artifacts.
    Expects in state:
      - 'script': the Octave .m script content as a string
      - 'spec': dict containing at least 'want_gif': bool
    Returns:
      - 'stdout': captured standard output from Octave
      - 'stderr': captured error output from Octave
      - 'frames': list of file paths to generated PNG frames
      - 'gif': file path to the combined GIF (or None if want_gif is False)
    """
    script = state.get("script")
    spec = state.get("spec", {})
    if script is None:
        raise ValueError("Executor requires 'script' in state")

    want_gif = spec.get("want_gif", False)

    # Create a unique run directory under test_runs/
    run_id = uuid.uuid4().hex
    run_dir = os.path.join("test_runs", run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Write the script to disk
    script_path = os.path.join(run_dir, "script.m")
    with open(script_path, "w") as f:
        f.write(script)

    # Invoke Octave to execute the script and collect frames
    result = run_octave(script_path, run_dir)
    frames = result.get("frames", [])

    # Optionally build a GIF from frames
    gif_path = None
    if want_gif and frames:
        gif_path = os.path.join(run_dir, "output.gif")
        make_gif(frames, gif_path)

    return {
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "frames": frames,
        "gif": gif_path,
    }