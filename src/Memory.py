import numpy as np
import os
from pathlib import Path
import json
import re
import cv2

# for now, we will use the current working directory; I need to get confirmation as to where 
# Professor M wants the files to be stored
main_path = Path.cwd() / "OpticalFlow"
# main_path = Path.home() / "Desktop" / "OpticalFlow"
types_path = main_path / "types.json"

def init_memory():
    """
    Initializes memory for the application.

    This creates a main folder 'OpticalFlow' on the user's Desktop, along with a 'types.json'
    file if it doesn't already exist.

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

def save_arrays(path, **arrays):
    """
    Saves multiple arrays to a compressed .npz file.
    
    Args:
        path (str): The file path where the arrays will be saved.
        **arrays: Named arrays to save. Each argument should be a NumPy array.

    Returns:
        None: The function saves the arrays to the specified path.
    
    Raises:
        PermissionError: If there is a permission issue when trying to save the file.
        FileNotFoundError: If the directory does not exist.
        TypeError: If any of the provided arrays are not NumPy arrays.
        Exception: For any other unexpected errors.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        for name, arr in arrays.items():
            if not isinstance(arr, np.ndarray):
                raise TypeError(f"'{name}' is not a NumPy array")
        np.savez_compressed(path, **arrays)

    except PermissionError:
        print(f"[ERROR] Permission denied while saving to: {path}")
    except FileNotFoundError:
        print(f"[ERROR] Directory not found for path: {path}")
    except TypeError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while saving: {e}")
    
    return None

def save_params(stack_type, params):
    """
    Saves the parameters for a given stack type to a JSON file.

    Args:
        stack_type (str): The type of the stack.

    Returns:
        None: The function saves the parameters to 'types.json'.
    
    Raises:
        ValueError: If the stack type is not recognized.
    """
    params = check_params(stack_type)
    
    with open(types_path, "r") as f:
        types = json.load(f)
    
    if stack_type not in types:
        types[stack_type] = params
        with open(types_path, "w") as f:
            json.dump(types, f, indent=2)

def check_params(stack_type):
    """
    Checks if the stack type is valid and returns the corresponding parameters.

    Args:
        stack_type (str): The type of the stack.

    Returns:
        dict: Parameters corresponding to the stack type.
    
    Raises:
        ValueError: If the stack type is not recognized.
    """
    with open(types_path, "r") as f:
        types = json.load(f)
    
    if stack_type not in types:
        types[stack_type] = { 'opt_flow ': {      'pyr_scale' : 0.5,
                                                    'levels' : 3,
                                                    'winsize' : 15,
                                                    'iterations' : 3,
                                                    'poly_n' : 5,
                                                    'poly_sigma' : 1.2,
                                                    'flags' : 0},
                                'process_args' : {  'gauss' : {'ksize': (5, 5), 'sigmaX': 1.5},
                                                    'median': {'ksize': 5},
                                                    'normalize': {'alpha': 0, 'beta': 255, 'norm_type': cv2.NORM_MINMAX},
                                                    'flags' : ['laplace']
                                }}
        with open(types_path, "w") as f:
            json.dump(types, f, indent=2)
    return types[stack_type]


def save_TiffStack(path, name, stack_type, arr, params):
    """
    Saves a TiffStack image to the OpticalFlow directory.

    Args:
        img (TiffStack): The TiffStack image object to save.

    Returns:
        None: The function saves the image and its metadata to a JSON file.
        """
    save_params(stack_type, params)

    file_path = main_path / name
    
    data = {
        "path": path,
        "stack_type": stack_type,
        "name": name
    }

    os.makedirs(file_path, exist_ok=True)
    meta_path = file_path / 'meta.json'
    np_path = file_path / 'arr.npy'

    with open(meta_path, 'w') as f:
        json.dump(data, f, indent=2)
    np.save(np_path, arr)


