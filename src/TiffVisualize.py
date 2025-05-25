import matplotlib.pyplot as plt

def show_flow(flow):
    step = 25
    Y, X = np.mgrid[0:flow.shape[0]:step, 0:flow.shape[1]:step]
    U = flow[::step, ::step, 0]  # dx
    V = flow[::step, ::step, 1]  # dy

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.quiver(X, Y, U, V, scale=200, pivot='tail', color='blue')
    plt.title("Optical Flow Vector Field")
    plt.xlim(0, flow.shape[1])
    plt.ylim(flow.shape[0], 0)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()

def show_image(image, title='Image'):
    """
    Displays an image using matplotlib.

    Args:
        image (np.ndarray): Image to display.
        title (str): Title of the window. Default is 'Image'.

    Returns:
        None: Just displays the image.
    """
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()