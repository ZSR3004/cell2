import matplotlib.pyplot as plt
import numpy as np

def show_flow(flow, title='Optical Flow'):
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

def show_image(image, title='Image', figsize=(12, 8)):
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