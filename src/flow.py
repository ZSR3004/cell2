import cv2
import numpy as np
from scipy.ndimage import gaussian_laplace
from multiprocessing import Pool, cpu_count

def preprocess_frame(args) -> np.ndarray:
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
    frame, kwargs = args
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

def preprocess_stack(arr: np.ndarray, **kwargs) -> np.ndarray:
    """
    Preprocesses a stack of frames with optional Gaussian/median blurs, normalization,
    and type conversion.

    Args:
        arr (np.ndarray): Input stack of frames (shape: N x H x W).
        **kwargs:
            - laplace (dict): {'sigma': float} for Gaussian Laplace filter
            - gauss (dict): {'ksize': (int, int), 'sigmaX': float}
            - median (dict): {'ksize': int}
            - normalize (dict): {'alpha': int, 'beta': int, 'norm_type': int}
            - convert (dict): {'dtype': np.dtype}
            - skip (list[str]): steps to skip (e.g., ['gauss', 'median'])

    Returns:
        np.ndarray: Preprocessed stack of frames.
    """

    frames = [(arr[i], kwargs) for i in range(arr.shape[0])]
    with Pool(cpu_count()) as pool:
        preprocessed_frames = pool.map(preprocess_frame, frames)
    return np.stack(preprocessed_frames, axis=0)

def combine_flows(flow_list : list) -> np.ndarray:
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

def compute_flow_pair(args) -> np.ndarray:
    """
    Computes optical flow for a pair of frames using Farneback method.

    Args:
        args (tuple): A tuple containing two frames and flow arguments.
            - f1: First frame (np.ndarray).
            - f2: Second frame (np.ndarray).
            - flow_args: Dictionary with parameters for optical flow calculation.
                - pyr_scale: float, scale factor for pyramid
                - levels: int, number of pyramid levels
                - winsize: int, size of the window for averaging
                - iterations: int, number of iterations at each pyramid level
                - poly_n: int, size of the pixel neighborhood
                - poly_sigma: float, standard deviation of the Gaussian used for polynomial expansion
                - flag: int, operation flags

    Returns:
        np.ndarray: Optical flow vectors for the pair of frames.
    """
    f1, f2, flow_args = args
    return cv2.calcOpticalFlowFarneback(
        f1, f2, None,
        flow_args['pyr_scale'],
        flow_args['levels'],
        flow_args['winsize'],
        flow_args['iterations'],
        flow_args['poly_n'],
        flow_args['poly_sigma'],
        flow_args['flag'])

def optical_flow(   arr : np.array,
                    pyr_scale : float = 0.5, 
                    levels : int = 3, 
                    winsize : int = 15,
                    iterations : int = 3, 
                    poly_n : int = 5, 
                    poly_sigma : float = 1.2,
                    flag : int = 0) -> np.ndarray:
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
 
    flow_args = {
        'pyr_scale': pyr_scale,
        'levels': levels,
        'winsize': winsize,
        'iterations': iterations,
        'poly_n': poly_n,
        'poly_sigma': poly_sigma,
        'flag': flag
    }
    pairs = [(arr[i], arr[i+1], flow_args) for i in range(arr.shape[0] - 1)]
    with Pool(cpu_count()) as pool:
        flow_list = pool.map(compute_flow_pair, pairs)
    return np.stack(flow_list)