import os
import json
import numpy as np
from pathlib import Path
import matplotlib.animation as animation
from .defaults import default_process, default_flow, default_trajectory

main_path = Path.cwd() / "CellFlow" # update this to make it desktop
inbox_path = main_path / "inbox"
types_path = main_path / "types.json"

def init_memory() -> None:
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

def get_unique_path(name, file_type, pattern_fn) -> Path:
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
   
# saving
def save_type(stacktype : str, params : dict) -> None:
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

def save_meta(path : str, stacktype : str, name : str) -> None:
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

def save_arr(name : str, arr : np.array) -> None:
    """
    Saves a numpy array to a file.
    
    Args:
        arr (np.array): The numpy array to save.
    
    Returns:
        None: Just saves the array to a file.
    """
    np.save(main_path / name, arr)

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
    file_path = get_unique_path(name, 'flow', lambda i: f"{name}_f{i}.npy")
    np.save(file_path, arr)

def save_trajectory(name : str, ftag : str, arr : np.array) -> None:
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
    def number_to_tag(number : int) -> str:
        tag = ''
        while True:
            tag = chr(ord('a') + number % 26) + tag
            number = number // 26
            if number == 0:
                break
        return tag

    file_path = get_unique_path(name, 'trajectory', lambda i: f"{name}_t{ftag}{number_to_tag(i)}.npy")
    np.save(file_path, arr)

def save_original_video(name : str, **kwargs) -> None:
    """
    Saves a video of image frames using matplotlib.
    Args:
        name (str): Name of the video file to save.
        **kwargs: Additional keyword arguments that include:
            - im: Matplotlib image display object for the original frames.
            - image_stack: Image stack of shape (T, H, W) or (T, H, W, 3) for RGB.
            - ax: Matplotlib axes object for the plot.
            - fig: Matplotlib figure object for the plot.
            - T: Total number of frames in the image stack.
            - fps: Frames per second for the video.
        Returns:
            None: Just saves the video to the specified path.
    """
    im = kwargs.get('im', None)
    image_stack = kwargs.get('image_stack', None)
    ax = kwargs.get('ax', None)
    fig = kwargs.get('fig', None)
    T = kwargs.get('T', image_stack.shape[0])
    fps = kwargs.get('fps', 10)

    file_path = get_unique_path(name, 'video', lambda i: f"{name}_vo_{i}.mp4")

    def update(frame):
        im.set_data(image_stack[frame])
        ax.set_title(f"Frame {frame}")

    ani = animation.FuncAnimation(fig, update, frames=T, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps)
    ani.save(file_path, writer=writer)

def save_vector_video(name : str, flag : str, **kwargs) -> None:
    """
    Creates a video of optical flow vectors overlaid on the original image frames.

    Args:
        name (str): Name of the video file to save.
        flag (str): Flag to determine the type of video being saved.
        **kwargs: Additional keyword arguments that include:
            - img_disp: Matplotlib image display object for the original frames.
            - arr: Optical flow array of shape (T, H, W, 2) where T is the number of frames,
                   H is height, W is width, and the last dimension contains the flow vectors (dx, dy).
            - og_arr: Original image frames array of shape (T, H, W, C). Default is None.
            - step: Step size for downsampling the flow vectors for visualization. Default is 20.
            - fps: Frames per second for the video. Default is 10.
            - quiver: Matplotlib quiver object for displaying flow vectors.
            - ax: Matplotlib axes object for the plot.
            - fig: Matplotlib figure object for the plot.
            - T_minus_1: Total number of frames minus one (T-1).
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
    quiver = kwargs.get('quiver', None)
    ax = kwargs.get('ax', None)
    fig = kwargs.get('fig', None)
    T = kwargs.get('T', None)

    if flag[0] not in ['f', 't']:
        raise ValueError(f'Invalid flag. Expected f or t, but got {flag}')

    file_path = get_unique_path(name, 'video', lambda i: f"{name}_v{flag}_{i}.mp4")
    
    def update(frame):
        U = arr[frame, ::step, ::step, 0]
        V = arr[frame, ::step, ::step, 1]
        quiver.set_UVC(U, V)

        if img_disp is not None:
            img_disp.set_data(og_arr[frame])

        ax.set_title(f"Frame {frame}")

    ani = animation.FuncAnimation(fig, update, frames=range(T), interval=1000/fps, blit=False)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist='Flow'), bitrate=1800)
    ani.save(file_path, writer=writer)

def load_params(stacktype : str) -> dict:
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