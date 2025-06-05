import cv2
import numpy as np
from scipy.ndimage import gaussian_laplace

def preprocess_frame(frame: np.ndarray, **kwargs) -> np.ndarray:
    """
    Preprocesses a single frame with optional Gaussian/median blurs, normalization,
    and type conversion.

    Args:
        frame (np.ndarray): Input image/frame.
        **kwargs:
            - laplace (dict): {'sigma': float} for Gaussian Laplace filter
            - gauss (dict): {'ksize': (int, int), 'sigmaX': float}
            - median (dict): {'ksize': int}
            - normalize (dict): {'alpha': int, 'beta': int, 'norm_type': int}
            - convert (dict): {'dtype': np.dtype}
            - skip (list[str]): steps to skip (e.g., ['gauss', 'median'])

    Returns:
        np.ndarray: Preprocessed image.
    """
    skip = kwargs.get("skip", [])

    if 'laplace' in skip:
        laplace_cfg = kwargs.get("laplace", {})
        sigma = laplace_cfg.get("sigma", 1.0)
        frame = gaussian_laplace(frame, sigma=sigma)

    if "gauss" not in skip:
        gauss_cfg = kwargs.get("gauss", {})
        ksize = gauss_cfg.get("ksize", (5, 5))
        sigmaX = gauss_cfg.get("sigmaX", 1.5)
        frame = cv2.GaussianBlur(frame, ksize, sigmaX)

    if "median" not in skip:
        median_cfg = kwargs.get("median", {})
        ksize = median_cfg.get("ksize", 5)
        frame = cv2.medianBlur(frame, ksize)

    if "normalize" not in skip:
        norm_cfg = kwargs.get("normalize", {})
        alpha = norm_cfg.get("alpha", 0)
        beta = norm_cfg.get("beta", 255)
        norm_type = norm_cfg.get("norm_type", cv2.NORM_MINMAX)
        frame = cv2.normalize(frame, None, alpha, beta, norm_type)

    if "convert" not in skip:
        frame = cv2.convertScaleAbs(frame)

    return frame

def combine_flows(flow_list : list):
    """
    Temporary function to combine different channels into one array.

    Args:
        flow_list (list[np.array]): List of numpy arrays to be combined.

    Returns:
        combined: combined stack of summed and orginal flows.
    """
    sum_arr = flow_list[0] + flow_list[1]
    combined = np.stack([sum_arr, flow_list[0], flow_list[1]], axis=1)
    return combined

def optical_flow(   arr : np.array,
                    pyr_scale : float = 0.5, 
                    levels : int = 3, 
                    winsize : int = 15,
                    iterations : int = 3, 
                    poly_n : int = 5, 
                    poly_sigma : float = 1.2,
                    flag : int = 0,
                    default = False):
    """
    Computes dense optical flow using Farneback method on a preprocessed channel. Allows manual
    changes to the params for optical flow.

    Args:
            - arr: np.arr, stack for optical flow processing
            - pyr_scale: float, scale factor for pyramid
            - levels: int, number of pyramid levels
            - winsize: int, size of the window for averaging
            - iterations: int, number of iterations at each pyramid level
            - poly_n: int, size of the pixel neighborhood
            - poly_sigma: float, standard deviation of the Gaussian used for polynomial expansion
            - flags: int, operation flags
            - **kwargs: dict with keys for preprocessing (see preprocess_frame)
                
    Returns:
        np.ndarray: (N-1, H, W, 2) flow vectors between frames.
    """ 
    num_frames, h, w = arr.shape
    flow = np.empty((num_frames - 1, h, w, 2), dtype=np.float32)
    
    for i in range(num_frames - 1):
        f1 = arr[i]
        f2 = arr[i + 1]
        flow[i] = cv2.calcOpticalFlowFarneback(f1, f2, None,
                                                pyr_scale, levels, 
                                                winsize, iterations, 
                                                poly_n, poly_sigma, 
                                                flag)

    return flow