import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cv2
from scipy.ndimage import gaussian_laplace
import time
import os
from .Memory import *
from .TiffVisualize import show_flow, show_image
from .Flow import *

class TiffStack():
    def __init__(self, path, stacktype, name = None, n_channels = 3, dtype = np.uint16):
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
        self.stacktype = stacktype
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

        self.params = load_params(self.stacktype)
        self.save_TiffStack()
    
    def _get_name(self):
        """
        Generates a name for the TiffStack based on the file name.
        
        Returns:
            str: Name of the TiffStack.
        """
        base = os.path.basename(self.path)
        stem = os.path.splitext(base)[0]
        return stem
    
    def save_TiffStack(self):
        """
        Saves TiffStack object into the "Optical Flow" folder.

        Args:
            None
        
        Returns:
            None, just saves the object.
        """
        save_type(self.stacktype, self.params)
        save_meta(self.path, self.stacktype, self.name)
        save_arr(self.name, self.arr)
    
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
    
    def optical_flow(self):
        """
        Computes optical flow between the first two channels of the TIFF stack using Farneback method.
        Args:
            None
        Returns:
            np.ndarray: (N-1, H, W, 2) flow vectors between frames.
        """
        flow = self.params['flow']
        process = self.params['process']

        processed_arr2 = np.stack([preprocess_frame(f, **kwargs) for f in self.isolate_channel(1)])
        processed_arr3 = np.stack([preprocess_frame(f, **kwargs) for f in self.isolate_channel(2)])

        flow_2 = self.experiment_optical_flow(processed_arr2,
                                            flow['pyr_scale'],
                                            flow['levels'],
                                            flow['winsize'],
                                            flow['iterations'],
                                            flow['poly_n'],
                                            flow['poly_sigma'],
                                            flow['flag'],
                                            **process)
        flow_3 = self.experiment_optical_flow(processed_arr3,
                                            flow['pyr_scale'],
                                            flow['levels'],
                                            flow['winsize'],
                                            flow['iterations'],
                                            flow['poly_n'],
                                            flow['poly_sigma'],
                                            flow['flag'],
                                            **process)
        
        combined = combine_flows([flow_2, flow_3])
        save_flow(self.name, combined)
        return combined