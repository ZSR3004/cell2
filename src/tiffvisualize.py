import cv2
import numpy as np
import matplotlib.pyplot as plt
from src.memory import save_original_video, save_vector_video

import matplotlib.animation as animation

# Simple Frame Display
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

# Kymograph
def plot_kymograph(line, ax=None, figsize=(10, 6), aspect='auto', cmap='PRGn', origin='upper', label='Kymograph', 
                   xlabel='Position along line', ylabel='Time (frame index)', title='Kymograph', show=True):
    """
    Plots a kymograph from a 2D array.

    Args:
        line (np.ndarray): 2D array representing the kymograph data.
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates a new figure.
        figsize (tuple): Size of the figure in inches (width, height).
        aspect (str): Aspect ratio of the plot. Default is 'auto'.
        cmap (str): Colormap to use for the kymograph. Default is 'PRGn'.
        origin (str): Origin of the plot. Default is 'upper'.
        label (str): Label for the colorbar.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        title (str): Title of the plot.
        show (bool): Whether to display the plot immediately.
    
    Returns:
        None: Just displays the kymograph.
    """
    if ax is None:
        plt.figure(figsize=figsize)
        ax = plt.gca()
    im = ax.imshow(line, aspect=aspect, cmap=cmap, origin=origin)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if show:
        plt.show()

def vector_kymograph(arr, values=['x dir'], method=np.median, combine=True):
    """
    Create and optionally combine kymographs from flow data.
    """
    if not any(val in values for val in ['x dir', 'y dir', 'mag', 'angle']):
        raise ValueError("values must be a subset of ['x dir', 'y dir', 'mag', 'angle']")
    if method not in [np.median, np.mean]:
        print("Warning: this function was not designed to work with methods other than np.median or np.mean")

    plots = []

    if 'x dir' in values or 'y dir' in values:
        temp = np.array([method(arr[i, :, :, :], axis=0) for i in range(arr.shape[0])])
        if 'x dir' in values:
            plots.append((temp[:, :, 0], 'X Direction Kymograph', 'X Component of Velocity (px/frame)', 'PRGn'))
        if 'y dir' in values:
            plots.append((temp[:, :, 1], 'Y Direction Kymograph', 'Y Component of Velocity (px/frame)', 'PRGn'))

    if 'mag' in values:
        mag_per_frame = np.linalg.norm(arr, axis=3)
        temp = np.array([method(mag_per_frame[i, :, :], axis=0) for i in range(arr.shape[0])])
        plots.append((temp, 'Magnitude Kymograph', 'Speed (px/frame)', 'BuPu'))

    if 'angle' in values:
        angles_per_frame = np.arctan2(arr[:, :, :, 1], arr[:, :, :, 0])
        temp = np.array([method(angles_per_frame[i, :, :], axis=0) for i in range(arr.shape[0])])
        plots.append((temp, 'Angle Kymograph', 'Direction (radians)', 'BuPu'))

    if combine:
        n = len(plots)
        fig, axs = plt.subplots(n, 1, figsize=(10, 4 * n))
        if n == 1:
            axs = [axs]  # Make iterable if only one subplot
        for ax, (data, title, label, cmap) in zip(axs, plots):
            plot_kymograph(data, ax=ax, show=False, title=title, label=label, cmap=cmap)
        plt.tight_layout()
        plt.show()
    else:
        for data, title, label, cmap in plots:
            plot_kymograph(data, title=title, label=label, cmap=cmap)

# Heatmap
def vector_magnitude_heatmaps(flow, normalize=True):
    """
    Computes magnitude heatmaps from a flow array of shape (frames, height, width, 2).

    Args:
        flow (np.ndarray): Array of shape (frames, height, width, 2) with (dx, dy) vectors.
        apply_colormap (bool): If True, returns heatmaps with color (BGR, 3-channel).
        normalize (bool): If True, normalizes magnitudes to 0–255 range for visualization.

    Returns:
        heatmaps (np.ndarray): Array of shape (frames, height, width) or (frames, height, width, 3)
                               depending on apply_colormap.
    """
    magnitudes = np.linalg.norm(flow, axis=-1)

    if normalize:
        heatmaps = []
        for frame in magnitudes:
            norm = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
            norm = norm.astype(np.uint8)
            heatmaps.append(norm)
        heatmaps = np.stack(heatmaps, axis=0)
    else:
        heatmaps = magnitudes
    return heatmaps

def save_heatmap_video(flow, output_path='heatmap_video.mp4', fps=10, normalize=True):
    """
    Saves a heatmap video (MP4) from a flow array using matplotlib.

    Parameters:
        flow (np.ndarray): Array of shape (frames, height, width, 2)
        output_path (str): Path to save the MP4 video
        fps (int): Frames per second of the output video
        normalize (bool): Whether to normalize magnitudes per frame

    TODO: Seperate memory saving part
    TODO: Save to proper path
    """
    heatmaps = vector_magnitude_heatmaps(flow, normalize=normalize)

    fig, ax = plt.subplots()
    im = ax.imshow(heatmaps[0], cmap='jet', animated=True)
    ax.axis('off')

    def update(frame_idx):
        im.set_array(heatmaps[frame_idx])
        return [im]

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(heatmaps),
        interval=1000 / fps,
        blit=True
    )
    ani.save(output_path, fps=fps, extra_args=['-vcodec', 'libx264'])
    plt.close(fig)

# Raw Data Video Creation
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