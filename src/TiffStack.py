import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cv2
from scipy.ndimage import gaussian_laplace
import time
import os
from .Memory import *
from .TiffVisualize import show_flow, show_image, save_optical_flow_video

default_process = {'gauss' : {'ksize': (5, 5), 'sigmaX': 1.5},
                                     'median': {'ksize': 5},
                                     'normalize': {'alpha': 0, 'beta': 255, 'norm_type': cv2.NORM_MINMAX},
                                     'flags' : ['laplace']}
default_flow = {'pyr_scale' : 0.5,
                                'levels' : 3,
                                'winsize' : 15,
                                'iterations' : 3,
                                'poly_n' : 5,
                                'poly_sigma' : 1.2,
                                'flag' : 0}
default_trajectory = {} # empty until properly implemented

class TiffStack():
    def __init__(self, path, stack_type, name = None, n_channels = 3, dtype = np.uint16):
        """
        Initializes a TiffStack object by loading a TIFF file and extracting its frames.
        Args:
            path (str): Path to the TIFF file.
            n_channels (int): Number of channels in the TIFF stack. Default is 3.
            dtype (np.dtype): Data type of the image frames. Default is np.uint16.
        
        Attributes:
            path (str): Path to the TIFF file.
            timestamp (str): Timestamp of when the TIFF file was loaded.
            tags (list): List of tags for each frame in the TIFF stack.
            arr (np.ndarray): 4D numpy array containing the image frames, shape is (n_frames, n_channels, height, width).
        """
        self.path = path
        self.stack_type = stack_type
        self.n_channels = n_channels
        self.dtype = dtype
        if name is None:
            self.name = self._get_name()
        else:
            self.name = name
        try:
            with tiff.TiffFile(path) as img:

                total_pages = len(img.pages)
                assert total_pages % n_channels == 0, f"Number of pages ({total_pages}) must be divisible by n_channels ({n_channels})"

                n_frames = total_pages // n_channels
                ref_shape = img.pages[0].shape
                ref_dtype = img.pages[0].dtype
                assert ref_dtype == dtype, f"Expected dtype {dtype}, but got {ref_dtype}"

                self.arr = np.empty((n_frames, n_channels, ref_shape[0], ref_shape[1]), dtype=dtype)
                for i in range(n_frames):
                    for c in range(n_channels):
                        page_idx = i * n_channels + c
                        self.arr[i, c] = img.pages[page_idx].asarray()

        except Exception as e:
            print(f"Error loading TIFF file: {e}")
        
        if not main_path.exists():
            init_memory() 

        self.params = check_params(self.stack_type)
        save_TiffStack(self.path, self.name, self.stack_type, self.arr, self.params)
        

    def _get_name(self):
        """
        Generates a name for the TiffStack based on the file name.
        
        Returns:
            str: Name of the TiffStack.
        """
        base = os.path.basename(self.path)
        stem = os.path.splitext(base)[0]
        return stem
    
    def isolate_channel(self, channel_idx : int):
        """
        Isolates a specific channel from the TIFF stack.

        Args:
            channel_idx (int): Index of the channel to isolate (0-indexed).

        Returns:
            np.ndarray: Isolated channel as a 3D numpy array.
        """
        assert 0 <= channel_idx < self.arr.shape[1], f"Channel index out of range: {channel_idx}"
        return self.arr[:, channel_idx, ...]

    def _preprocess_frame(self, frame: np.ndarray, **kwargs) -> np.ndarray:
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
    
    def optical_flow(self):
        """
        Computes optical flow between the first two channels of the TIFF stack using Farneback method.
        Args:
            None
        Returns:
            np.ndarray: (N-1, H, W, 2) flow vectors between frames."""
        opt_flow = self.params['opt_flow']
        process_args = self.params['process_args']
        flow_2 = self.experiment_optical_flow(1,
                                            opt_flow['pyr_scale'],
                                            opt_flow['levels'],
                                            opt_flow['winsize'],
                                            opt_flow['iterations'],
                                            opt_flow['poly_n'],
                                            opt_flow['poly_sigma'],
                                            opt_flow['flag'],
                                            **process_args)
        flow_3 = self.experiment_optical_flow(2,
                                            opt_flow['pyr_scale'],
                                            opt_flow['levels'],
                                            opt_flow['winsize'],
                                            opt_flow['iterations'],
                                            opt_flow['poly_n'],
                                            opt_flow['poly_sigma'],
                                            opt_flow['flag'],
                                            **process_args)
        
        sum_arr = flow_2 + flow_3
        combined = np.stack([sum_arr, flow_2, flow_3], axis=1)
        save_flow(self.name, combined)
        return combined

    def experiment_optical_flow(self, channel_idx : int,
                     pyr_scale : float = 0.5, 
                     levels : int = 3, 
                     winsize : int = 15,
                     iterations : int = 3, 
                     poly_n : int = 5, 
                     poly_sigma : float = 1.2,
                     flag : int = 0, 
                     **kwargs):
        """
        Computes dense optical flow using Farneback method on a preprocessed channel. Allows manual
        changes to the params for optical flow.

        Args:
            channel_idx (int): Channel index from TIFF stack.
                - pyr_scale: float, scale factor for pyramid
                - levels: int, number of pyramid levels
                - winsize: int, size of the window for averaging
                - iterations: int, number of iterations at each pyramid level
                - poly_n: int, size of the pixel neighborhood
                - poly_sigma: float, standard deviation of the Gaussian used for polynomial expansion
                - flags: int, operation flags
                - **kwargs: dict with keys for preprocessing (see _preprocess_frame)
                    
        Returns:
            np.ndarray: (N-1, H, W, 2) flow vectors between frames.
        """ 
        arr = self.isolate_channel(channel_idx)
        preprocessed = np.stack([self._preprocess_frame(f, **kwargs) for f in arr])
        num_frames, h, w = preprocessed.shape

        flow = np.empty((num_frames - 1, h, w, 2), dtype=np.float32)
        for i in range(num_frames - 1):
            f1 = preprocessed[i]
            f2 = preprocessed[i + 1]
            flow[i] = cv2.calcOpticalFlowFarneback(f1, f2, None,
                                                   pyr_scale, levels, 
                                                   winsize, iterations, 
                                                   poly_n, poly_sigma, 
                                                   flag)
        return flow