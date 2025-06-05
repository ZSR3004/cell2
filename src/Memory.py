import os
from pathlib import Path
import json
import numpy as np
import matplotlib.animation as animation
from .Defaults import default_process, default_flow, default_trajectory

main_path = Path.cwd() / "CellFlow" # update this to make it desktop
inbox_path = main_path / "inbox"
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
        os.makedirs(inbox_path, exist_ok=True)
        with open(types_path, "w") as f:
            json.dump({}, f, indent=2)

    except Exception as e:
        print(f"[ERROR] Failed to initialize memory: {e}")
   
# saving
def save_type(stacktype : str, params : dict):
    """
    Saves the type of stack to the types.json file.
    
    Args:
        stacktype (str): The type of stack to save.
        **kwargs: Additional keyword arguments that can include:
            - process: parameters for preprocessing the stack.
            - flow: parameters for optical flow calculation.
            - trajectory: parameters for trajectory calculation.
    
    Returns:
        None: Just saves the type to the types.json file.
    """
    with open(types_path, 'r') as f:
        types = json.load(f)

    types[stacktype] = params

    with open(types_path, 'w') as f:
        json.dump(types, f, indent=2)

def save_meta(path : str, stacktype : str, name : str):
    """
    Saves metadata about the stack to a JSON file.
    Args:
        path (str): The path where the metadata file will be saved.
        stacktype (str): The type of the stack.
        name (str): The name of the stack.

    Returns:
        None: Just saves the metadata to the specified path.
    """
    meta = {'path' : path, 'stacktype' : stacktype, 'name' : name}
    meta_path = main_path / name
    meta_path.mkdir(parents=True, exist_ok=True)
    with open(meta_path / 'meta.json', 'w') as f:
        json.dump(meta, f, indent=2)

def save_arr(name : str, arr : np.array):
    """
    Saves a numpy array to a file.
    
    Args:
        arr (np.array): The numpy array to save.
    
    Returns:
        None: Just saves the array to a file.
    """
    np.save(main_path / name, arr)

def get_unique_path(name, file_type, pattern_fn):
    """
    Generates a unique file path in the given directory based on a naming pattern.

    Args:
        name (str): Main identifier (e.g., protein name).
        file_type (str): Subdirectory (e.g., 'flow', 'trajectory').
        pattern_fn (callable): Function that takes an integer and returns a file name.

    Returns:
        Path: Unique file path that does not yet exist.
    """
    save_dir = main_path / name / file_type
    save_dir.mkdir(parents=True, exist_ok=True)

    i = 0
    while True:
        file_name = pattern_fn(i)
        file_path = save_dir / file_name
        if not file_path.exists():
            return file_path
        i += 1

def save_flow(name : str, arr : np.array):
    """
    Saves the optical flow array.
    
    Args:
        name (str): The name of the file.
        arr (np.array): The optical flow or trajectory array to save, expected to be of shape (T, H, W, 2)
            where T is the number of frames, H is height, W is width, and the last dimension contains
            the flow vectors (dx, dy) or trajectory vectors.
    
    Returns:
        None: Just saves the array to a file.
    """
    file_path = get_unique_path(name, lambda i: f"{name}_f{i}.npy")
    np.save(file_path, arr)

def save_trajectory(name : str, ftag : str, arr : np.array):
    """
    Saves the trajectory flow array.

    Args:
        name (str): The name of the file.
        arr (np.array): The optical flow or trajectory array to save, expected to be of shape (T, H, W, 2)
        ftag (str): The tag associated with the optical flow file the trajectory was derived from.
            where T is the number of frames, H is height, W is width, and the last dimension contains
            the flow vectors (dx, dy) or trajectory vectors.
    
    Returns:
        None: Just saves the array to a file.
    """
    def number_to_tag(number):
        tag = ''
        while True:
            tag = chr(ord('a') + number % 26) + tag
            number = number // 26
            if number == 0:
                break
        return tag

    def tag_exists(tag):
        file_name = f"{name}_{ftag}{tag}.npy"
        file_path = save_dir / file_name
        return file_path.exists()

    file_path = get_unique_path(name, lambda i: f"{name}_t{ftag}{number_to_tag(i)}.npy")
    np.save(file_path, arr)

def save_video(name : str, flag : str, **kwargs):
    """
    Creates a video of optical flow vectors overlaid on the original image frames.

    Args:
        name (str): Name of the video file to save.
        flag (str): Flag to determine the type of video being saved.
        **kwargs: Additional keyword arguments that include:
            - img_disp (matplotlib.image.AxesImage): Image display object for the original frames.
            - arr (np.ndarray): Optical flow array of shape (T, H, W, 2) where T is the number of frames,
                H is height, W is width, and the last dimension contains the flow vectors (dx, dy).
            - og_arr (np.ndarray): Original image frames array of shape (T, H, W, C).
            - step (int): Step size for downsampling the flow vectors for visualization.
            - fps (int): Frames per second for the video.
            - figsize (tuple): Figure size in inches (width, height).
            - title (str): Title of the video.
            - quiver (matplotlib.quiver.Quiver): Quiver object for displaying flow vectors.
            - ax (matplotlib.axes.Axes): Axes object for the plot.
            - fig (matplotlib.figure.Figure): Figure object for the plot.
            - T_minus_1 (int): Total number of frames minus one.
    Returns:
        None: Just saves the video to the specified path.

    Invariant:
        Assumes, that all values are present in kwargs and are of the correct type. The check occurs in the
        `create_optical_flow_video` function (in TiffVisualize.py) before this function is called.
    """
    img_disp = kwargs.get('img_disp', None)
    arr = kwargs.get('arr', None)
    og_arr = kwargs.get('og_arr', None)
    step = kwargs.get('step', None)
    fps = kwargs.get('fps', None)
    figsize = kwargs.get('figsize', None)
    title = kwargs.get('title', None)
    quiver = kwargs.get('quiver', None)
    ax = kwargs.get('ax', None)
    fig = kwargs.get('fig', None)
    T_minus_1 = kwargs.get('T_minus_1', None)

    if flag[0] not in ['f', 't']:
        raise ValueError(f'Invalid flag. Expected f or t, but got {flag}')

    file_path = get_unique_path(name, lambda i: f"{name}_v{flag}_{i}.mp4")
    
    def update(frame):
        img_disp.set_data(og_arr[frame])
        U = arr[frame, ::step, ::step, 0]
        V = arr[frame, ::step, ::step, 1]
        quiver.set_UVC(U, V)
        if title == None:
            ax.set_title(f'Frame {frame}')
        else:
            ax.set_title(f'{title} Frame {frame}')
        return img_disp, quiver
    
    
    ani = animation.FuncAnimation(fig, update, frames=T_minus_1, blit=False)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist='Optical Flow'), bitrate=1800)
    ani.save(file_path, writer=writer)

def load_params(stacktype : str):
    """
    Loads parameters from types.json.

    Args:
        stacktype: The type of cell.
    
    Returns:
        params: Dictionary of parameters.
    """
    with open(types_path, 'r') as f:
        types = json.load(f)
    
    if stacktype not in types:
        params = {'process' : default_process, 'flow' : default_flow, 'trajectory' : default_trajectory}
    else:
        params = types[stacktype]

    return params