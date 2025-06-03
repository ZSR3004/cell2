import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2

def show_flow(flow : np.array, title='Optical Flow'):
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

def show_image(image : np.array, title='Image', figsize=(12, 8)):
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

def create_optical_flow_video(name : str, arr : np.array, og_arr : np.array, 
                              step : int = 20, scale : int = 1, fps : int = 10, figsize : (int, int) = (12,8),
                              title : str = None, flag : str = None):
    """
    Creates a video of optical flow vectors overlaid on the original image frames. 

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
    if flag != "" or flag != 'f' or flag != 't':
        raise ValueError('Invalid video type. Valid types are emoty quotes, an l or a t.')

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

    plt.close(fig)