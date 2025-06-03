import os
from pathlib import Path
import json

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
def save_type():
    pass

def save_meta():
    pass

def save_arr():
    pass

def save_flow():
    pass

def save_trajectory():
    pass

def save_video():
    pass

# loading
def load_type():
    pass

def load_meta():
    pass

def load_arr():
    pass

def load_flow():
    pass

def load_trajectory():
    pass