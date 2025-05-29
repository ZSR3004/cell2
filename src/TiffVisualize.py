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

def save_optical_flow_video(optical_flow : np.array, image_stack : np.array, 
                            output_file, step=20, scale=1, fps=10):
    """
    Saves an MP4 video showing optical flow vector fields over time.
    
    Args:
        - optical_flow: np.ndarray of shape (T-1, H, W, 2)
        - image_stack: np.ndarray of shape (T, H, W)
        - step: int, grid spacing for arrows
        - scale: float, scale factor for quiver arrows
        - output_file: str, name of the output MP4 file
        - fps: int, frames per second for the video
    
    Returns:
        None, saves the video to the specified output file.
    
    TODO:
        - Make more visible by changing color, vector sizes, etc.
    """
    T_minus_1, H, W, _ = optical_flow.shape
    Y, X = np.mgrid[0:H:step, 0:W:step]

    fig, ax = plt.subplots(figsize=(12, 8))
    img_disp = ax.imshow(image_stack[0], cmap='gray', origin='upper')
    quiver = ax.quiver(X, Y, optical_flow[0, ::step, ::step, 0],
                             optical_flow[0, ::step, ::step, 1],
                             color='red', angles='xy', scale_units='xy', scale=scale)
    ax.axis('off')
    ax.set_title('Optical Flow Frame 0')

    def update(frame):
        img_disp.set_data(image_stack[frame])
        U = optical_flow[frame, ::step, ::step, 0]
        V = optical_flow[frame, ::step, ::step, 1]
        quiver.set_UVC(U, V)
        ax.set_title(f'Optical Flow Frame {frame}')
        return img_disp, quiver

    ani = animation.FuncAnimation(fig, update, frames=T_minus_1, blit=False)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist='Optical Flow'), bitrate=1800)
    ani.save(output_file, writer=writer)

    plt.close(fig)