import cv2
import numpy as np
from scipy.ndimage import gaussian_laplace

def reconstruction_error(frame1, frame2):
    """
    Calculate the reconstruction error between two frames.
    Params:
        frame1: First frame (numpy array).
        frame2: Second frame (numpy array).
    Returns:
        Mean absolute error between the two frames.
    """
    error = np.abs(frame1 - frame2)
    return np.mean(error)

def smoothness_constraint(frame1, frame2):
    """
    Calculate the smoothness constraint between two frames.
    This function computes the Laplacian of Gaussian for both frames
    and returns the sum of their absolute differences.
    Params:
        frame1: First frame (numpy array).
        frame2: Second frame (numpy array).
    Returns:
        Sum of absolute differences of the Laplacian of Gaussian of both frames.
    """
    laplacian1 = gaussian_laplace(frame1, sigma=1)
    laplacian2 = gaussian_laplace(frame2, sigma=1)
    
    return np.sum(np.abs(laplacian1 - laplacian2))

