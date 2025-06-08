import os
import numpy as np
import tifffile as tiff
import src.flow as flow
import src.memory as mem
import src.trajectory as traj
from .tiffvisualize import create_vector_field_video, create_orginal_video
from .defaults import default_process, default_flow, default_trajectory

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
        
        if not mem.main_path.exists():
            mem.init_memory() 

        self.params = mem.load_params(self.stacktype)
        self.save_TiffStack()
    
    def _get_name(self) -> str:
        """
        Generates a name for the TiffStack based on the file name.
        
        Returns:
            str: Name of the TiffStack.
        """
        base = os.path.basename(self.path)
        stem = os.path.splitext(base)[0]
        return stem
    
    def save_TiffStack(self) -> None:
        """
        Saves TiffStack object into the "Optical Flow" folder.

        Args:
            None
        
        Returns:
            None, just saves the object.
        """
        mem.save_type(self.stacktype, self.params)
        mem.save_meta(self.path, self.stacktype, self.name)
        mem.save_arr(self.name, self.arr)
    
    def isolate_channel(self, channel_idx : int) -> np.ndarray:
        """
        Isolates a specific channel from the TIFF stack.

        Args:
            channel_idx (int): Index of the channel to isolate (0-indexed).

        Returns:
            np.ndarray: Isolated channel as a 3D numpy array.
        """
        assert 0 <= channel_idx < self.arr.shape[1], f"Channel index out of range: {channel_idx}"
        return self.arr[:, channel_idx, ...]
    
    def calculate_optical_flow(self, process_args=None, flow_args=None, default=False) -> np.ndarray:
        """
        Computes optical flow between the first two channels of the TIFF stack using the Farneback method.

        Args:
            process_args (dict): Preprocessing steps and parameters.
            flow_args (dict): Parameters for optical flow calculation.
            default (bool): Use default optical flow parameters if True.

        Returns:
            np.ndarray: Combined flow vectors of shape (N-1, H, W, 2).
        """
        if process_args is None:
            process_args = self.params.get('preprocess', default_process)
        if flow_args is None:
            flow_args = self.params.get('optical_flow', default_flow)

        def compute_flow_for_channel(channel_idx):
            frames = self.isolate_channel(channel_idx)
            processed = flow.preprocess_stack(frames, **process_args)
            if default:
                return flow.optical_flow(processed)
            else:
                return flow.optical_flow(
                    processed,
                    flow_args['pyr_scale'],
                    flow_args['levels'],
                    flow_args['winsize'],
                    flow_args['iterations'],
                    flow_args['poly_n'],
                    flow_args['poly_sigma'],
                    flow_args['flag']
                )

        flow_2 = compute_flow_for_channel(1)
        flow_3 = compute_flow_for_channel(2)

        combined = flow.combine_flows([flow_2, flow_3])
        mem.save_flow(self.name, combined)
        return combined
    
    def save_orginal_video(self, idx : int = 0, 
                           figsize : int | int = (12, 8), fps : int = 10, cmap : str = 'gray') -> None:
        """
        Saves a video of the original image frames from the TIFF stack.

        Args:
            idx (int): Index of the channel to visualize. Default is 0.
            figsize (tuple): Figure size in inches (width, height). Default is (12, 8).

        Returns:
            None
        """
        og_arr = self.isolate_channel(idx)
        create_orginal_video(self.name, og_arr, figsize=figsize, fps=fps, cmap=cmap)

    def save_optflow_video(self, flow, idx : int = 0, step : int = 20, 
                          scale : int = 500, color : str = 'blue', fps : int = 10, 
                          figsize : int | int = (12,8),
                          title : str = None, overlay : bool = False) -> None:
        
        if overlay:
            og_arr = self.isolate_channel(idx)
        else:
            og_arr = None 

        create_vector_field_video(
            self.name, 
            flow[:, idx, ...], 
            og_arr, 
            step=step, 
            scale=scale,
            color=color, 
            fps=fps, 
            figsize=figsize, 
            title=title,
            flag='f'
        )
    
    def calculate_trajectory(self, flow) -> np.ndarray:
        """
        Calculates the trajectory of the optical flow vectors.

        Returns:
            np.ndarray: Trajectory of the optical flow vectors.
        """
        return traj.trajectory(flow)