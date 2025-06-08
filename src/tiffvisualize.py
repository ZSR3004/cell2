import numpy as np
from .memory import save_video
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

def show_image(image : np.array, title='Image', figsize=(12, 8)) -> None:
    """
    Displays an image using matplotlib.

    Args:
        image (np.ndarray): Image to display.
        title (str): Title of the window. Default is 'Image'.
        figsize (tuple): Figure size in inches (width, height). Default is (12, 8).

    Returns:
        None: Just displays the image.
    """
    plt.figure(figsize=figsize)
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()

def show_flow(flow : np.array, title='Optical Flow') -> None:
    """
    Displays optical flow as a quiver plot using matplotlib.

    Args:
        flow (np.ndarray): Optical flow array of shape (H, W, 2) where H is height, W is width,
                           and the last dimension contains the flow vectors (dx, dy).
        title (str): Title of the plot. Default is 'Optical Flow'.

    Returns:
        None: Just displays the plot.
    """
    step = 25
    Y, X = np.mgrid[0:flow.shape[0]:step, 0:flow.shape[1]:step]
    U = flow[::step, ::step, 0]  # dx
    V = flow[::step, ::step, 1]  # dy

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.quiver(X, Y, U, V, scale=200, pivot='tail', color='blue')
    plt.title(title)
    plt.xlim(0, flow.shape[1])
    plt.ylim(flow.shape[0], 0)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()

def save_image_video(image_stack: np.ndarray, output_path='image_video.mp4', fps=10, cmap='gray'):
    """
    Saves a video of image frames using matplotlib.

    Args:
        image_stack (np.ndarray): Image stack of shape (T, H, W) or (T, H, W, 3) for RGB.
        output_path (str): Path to save the video.
        fps (int): Frames per second.
        cmap (str): Colormap for grayscale images.

    Returns:
        None
    """
    T = image_stack.shape[0]
    is_grayscale = image_stack.ndim == 3  # (T, H, W)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    im = ax.imshow(image_stack[0], cmap=cmap if is_grayscale else None)

    def update(frame):
        im.set_data(image_stack[frame])
        ax.set_title(f"Frame {frame}")

    ani = FuncAnimation(fig, update, frames=T, interval=1000/fps, blit=False)
    writer = FFMpegWriter(fps=fps)
    ani.save(output_path, writer=writer)
    plt.close(fig)
    print(f"Video saved to {output_path}")

def save_flow_video(flow_stack: np.ndarray, output_path='optical_flow.mp4', fps=10,
                    image_stack: np.ndarray = None, step=25, scale=500):
    """
    Saves a video of optical flow (quiver animation), optionally overlaid on image frames.

    Args:
        flow_stack (np.ndarray): Flow of shape (T, H, W, 2).
        output_path (str): File path to save the video.
        fps (int): Frames per second of the video.
        image_stack (np.ndarray, optional): Matching image stack (T, H, W) or (T, H, W, 3).
        step (int): Sampling step for quiver vectors.
        scale (float): Scale of the arrows.

    Returns:
        None
    """
    T, H, W, _ = flow_stack.shape
    Y, X = np.mgrid[0:H:step, 0:W:step]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Optical Flow")
    ax.set_aspect('equal')
    ax.axis('off')

    if image_stack is not None:
        is_gray = image_stack.ndim == 3
        im = ax.imshow(image_stack[0], cmap='gray' if is_gray else None)
    else:
        im = None

    U = flow_stack[0, ::step, ::step, 0]
    V = flow_stack[0, ::step, ::step, 1]
    quiv = ax.quiver(X, Y, U, V, scale=scale, pivot='tail', color='blue')

    def update(frame):
        U = flow_stack[frame, ::step, ::step, 0]
        V = flow_stack[frame, ::step, ::step, 1]
        quiv.set_UVC(U, V)

        if im is not None:
            im.set_data(image_stack[frame])

        ax.set_title(f"Frame {frame}")

    ani = FuncAnimation(fig, update, frames=T, interval=1000/fps, blit=False)
    writer = FFMpegWriter(fps=fps)
    ani.save(output_path, writer=writer)
    plt.close(fig)
    print(f"Saved flow video to {output_path}")

def create_vector_field_video(name : str, arr : np.array, og_arr : np.array, 
                              step : int = 20, scale : int = 1, fps : int = 10, figsize : int | int = (12,8),
                              title : str = None, flag : str = None) -> None:
    """
    Creates a video of vector fields overlaid on the original image frames if desired. 

    Args:
        name (str): Name of the video file to save.
        arr (np.ndarray): Optical flow array of shape (T, H, W, 2) where T is the number of frames,
                          H is height, W is width, and the last dimension contains the flow vectors (dx, dy).
        og_arr (np.ndarray): Original image frames of shape (T, H, W, C) where C is the number of channels.
        step (int): Step size for downsampling the flow vectors for visualization. Default is 20.
        scale (int): Scale factor for the quiver arrows. Default is 1.
        fps (int): Frames per second for the video. Default is 10.
        figsize (tuple): Size of the figure in inches. Default is (12, 8).
        title (str): Title for the video frames. Default is None.
        flag (str): Video type flag. Valid values are empty string, 'f' for optical flow, or 't' for trajectories.
                    The empty string is used to denote you don't want the video saved.
        
    Returns:
        None: Just saves displays the video and saves it if desired.
    
    TODO:
        - Make more visible by changing color, vector sizes, etc.
    """
    if flag != "" and flag != 'f' and flag != 't':
        raise ValueError('Invalid video type. Valid types are empty quotes, an f or a t.')

    T_minus_1, H, W, _ = arr.shape
    Y, X = np.mgrid[0:H:step, 0:W:step]

    fig, ax = plt.subplots(figsize=figsize)
    img_disp = ax.imshow(og_arr[0], cmap='gray', origin='upper')
    quiver = ax.quiver(X, Y, arr[0, ::step, ::step, 0],
                             arr[0, ::step, ::step, 1],
                              color='red', angles='xy', scale_units='xy', scale=scale)
    ax.axis('off')
    if title == None:
        ax.set_title('Frame 0')
    else:
        ax.set_title(f'title Frame 0')

    if flag != "":
        save_video(name, flag, 
                   **{
                          'img_disp': img_disp,
                          'arr': arr,
                          'og_arr': og_arr,
                          'step': step,
                          'fps': fps,
                          'figsize': figsize,
                          'title': title,
                          'quiver': quiver,
                          'ax': ax,
                          'fig': fig,
                          'T_minus_1': T_minus_1
                   })

    plt.close(fig)