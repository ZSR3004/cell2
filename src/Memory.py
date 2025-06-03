import os
from pathlib import Path
import json
import numpy as np
import matplotlib.animation as animation

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

def get_out_path(name : str, flag : str):
    """
    Constructs the output path for saving files based on the provided name and flag.

    Args:
        name (str): The name of the file to be saved.
        flag (str): A flag indicating the type of file.
            - 'f': Flow file (np array)
            - 't': Trajectory file (np array)
            - 'vf': Video of flow vectors (mp4)
            - 'vt': Video of trajectory (mp4)

    Returns:
        str: The full path where the file will be saved.
    """
    if flag == 'f':
        designation = 'flow'
        file_end = '.npy'
    elif flag == 't':
        designation = 'trajectory'
        file_end = '.npy'
    elif flag == 'vf' or flag == 'vt':
        designation = 'video'
        file_end = '.mp4'
    else:
        raise ValueError(f"Unknown flag: {flag}. Expected 'f', 't', 'vf', or 'vt'.")

    save_dir = main_path / name / designation
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)

    i = 0
    while True:
        file_name = f"{name}_{flag}{i}{file_end}"
        file_path = save_dir / file_name
        if not file_path.exists():
            return file_path
        i += 1

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


    output_file = get_out_path(name, flag)
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
    ani.save(output_file, writer=writer)

# loading
def load_type(stacktype : str):
    pass

def load_arr(arr : np.array):
    pass

def load_flow(flow_arr : np.array):
    pass

def load_trajectory(trajectory_arr : np.array):
    pass