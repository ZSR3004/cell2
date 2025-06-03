import os
from pathlib import Path
import json
import numpy as np

main_path = Path.home() / "Desktop" / "Cell Flow Tracking"
types_path = main_path / "types.json"

def init_memory():
    """
    Initializes memory for the application.

    This creates a main folder 'OpticalFlow' on the user's Desktop, along with a 'types.json'
    file if it doesn't already exist.

    You can find a detailed description of this directory's structure under the README on Github.

    Args:
        None

    Returns:
        None
    """
    try:
        os.makedirs(main_path, exist_ok=True)
        if not types_path.exists():
            with open(types_path, "w") as f:
                json.dump({}, f, indent=2) 
    
    except Exception as e:
        print(f"[ERROR] Failed to initialize memory: {e}")

# saving
def save_type(  stacktype : str, **kwargs):
    pass

def save_meta(path : str, stacktype : str, name : str):
    pass

def save_arr(arr : np.array):
    pass

def save_flow(flow_arr : np.array):
    pass

def save_trajectory(trajectory_arr : np.array):
    pass

def save_video():
    pass

# loading
def load_type(stacktype : str):
    pass

def load_arr(arr : np.array):
    pass

def load_flow(flow_arr : np.array):
    pass

def load_trajectory(trajectory_arr : np.array):
    pass