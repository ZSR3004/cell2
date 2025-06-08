import numpy as np
from .memory import save_original_video, save_vector_video
import matplotlib.pyplot as plt

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

def show_flow(flow : np.array, title='Optical Flow', 
              step : int = 25, figsize : int | int = (12,6), scale : int = 200, 
              pivot : str = 'tail', color : str = 'blue') -> None:
    """
    Displays optical flow as a quiver plot using matplotlib.

    Args:
        flow (np.ndarray): Optical flow array of shape (H, W, 2) where H is height, W is width,
                           and the last dimension contains the flow vectors (dx, dy).
        title (str): Title of the plot. Default is 'Optical Flow'.
        step (int): Step size for downsampling the flow vectors for visualization. Default is 25.
        figsize (tuple): Size of the figure in inches (width, height). Default is (12, 6).
        scale (float): Scale factor for the quiver arrows. Default is 200.
        pivot (str): Pivot point for the arrows. Default is 'tail'.
        color (str): Color of the arrows. Default is 'white'.

    Returns:
        None: Just displays the plot.
    """
    Y, X = np.mgrid[0:flow.shape[0]:step, 0:flow.shape[1]:step]
    U = flow[::step, ::step, 0]  # dx
    V = flow[::step, ::step, 1]  # dy

    # Create plot
    plt.figure(figsize=figsize)
    plt.quiver(X, Y, U, V, scale=scale, pivot=pivot, color=color)
    plt.title(title)
    plt.xlim(0, flow.shape[1])
    plt.ylim(flow.shape[0], 0)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()

def create_orginal_video(name, image_stack: np.ndarray, 
                         figsize : int | int = (12, 8), fps : int = 10, cmap : str = 'gray') -> None:
    """
    Saves a video of image frames using matplotlib.

    Args:
        name (str): Name of the video file to save.
        image_stack (np.ndarray): Image stack of shape (T, H, W) or (T, H, W, 3) for RGB.
                                 T is the number of frames, H is height, W is width.
        figsize (tuple): Figure size in inches (width, height). Default is (12, 8).
        fps (int): Frames per second for the video. Default is 10.
        cmap (str): Colormap to use for grayscale images. Default is 'gray'.

    Returns:
        None
    """
    T = image_stack.shape[0]
    is_grayscale = image_stack.ndim == 3  # (T, H, W)
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    im = ax.imshow(image_stack[0], cmap=cmap if is_grayscale else None)

    save_original_video(name, 
                        **{
                            'im': im,
                            'image_stack': image_stack,
                            'ax': ax,
                            'fig': fig,
                            'T': T,
                            'fps': fps
                        })
    
    plt.close(fig)

def create_vector_field_video(name, arr : np.ndarray, og_arr : np.ndarray=None, 
                    step : int = 20, scale : int = 500, color : str = 'blue', 
                    fps : int = 10, figsize : int | int = (12,8),
                    title : str = None, flag : str = None) -> None:
    """
    Saves a video of optical flow (quiver animation), optionally overlaid on image frames.

    Args:
        name (str): Name of the video file to save.
        arr (np.ndarray): Optical flow array of shape (T, H, W, 2) where T is the number of frames,
                          H is height, W is width, and the last dimension contains the flow vectors (dx, dy).
        og_arr (np.ndarray): Original image frames array of shape (T, H, W, C). Default is None.
        step (int): Step size for downsampling the flow vectors for visualization. Default is 20.
        scale (int): Scale factor for the quiver arrows. Default is 500.
        color (str): Color of the arrows. Default is 'blue'.
        fps (int): Frames per second for the video. Default is 10.
        figsize (tuple): Figure size in inches (width, height). Default is (12, 8).
        title (str): Title of the video. Default is None.
        flag (str): Flag to determine if the video should be saved ('f' for flow, 't' for trajectory). Default is None.

    Returns:
        None
    """
    T, H, W, _ = arr.shape
    Y, X = np.mgrid[0:H:step, 0:W:step]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Optical Flow")
    ax.set_aspect('equal')
    ax.axis('off')

    if og_arr is not None:
        is_gray = og_arr.ndim == 3
        img_disp = ax.imshow(og_arr[0], cmap='gray' if is_gray else None)
    else:
        img_disp = None

    U = arr[0, ::step, ::step, 0]
    V = arr[0, ::step, ::step, 1]
    quiver = ax.quiver(X, Y, U, V, scale=scale, pivot='tail', color=color)

    if flag != "":
        save_vector_video(name, flag, 
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
                          'T': T
                   })

    plt.close(fig)