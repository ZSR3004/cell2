import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cv2
from scipy.ndimage import gaussian_laplace
import time

class TiffStack():
    def __init__(self, path, n_channels = 3, dtype = np.uint16):
        self.path = path
        self.date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            with tiff.TiffFile(path) as img:
                self.tags = []

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
                    self.tags.append([img.pages[i * n_channels + c].tags for c in range(n_channels)])

        except Exception as e:
            print(f"Error loading TIFF file: {e}")


    def isolate_channel(self, channel_idx):
        """
        Isolates a specific channel from the TIFF stack.

        Args:
            channel_idx (int): Index of the channel to isolate (0-indexed).

        Returns:
            np.ndarray: Isolated channel as a 3D numpy array.
        """
        assert 0 <= channel_idx < self.arr.shape[1], f"Channel index out of range: {channel_idx}"
        return self.arr[:, channel_idx, ...]

    def play_video(self, channel_idx = 0, delay = 30):
        """
        Plays video of the "channel_idx"th channel in the tiff stack. Press 'q' to quit, 'space' to pause/play, 
        left/right arrow keys to navigate frames.
        
        Args:
            channel_idx (int): Index of the channel to play (0-indexed).
            delay (int): Delay in milliseconds between frames. Default is 30.

        Returns:
            None: Just plays the video
        """
        assert 0 <= channel_idx < self.arr.shape[1], f"Channel index out of range: {channel_idx}"
        channel_stack = self.arr[:, channel_idx, ...]
        total_frames = channel_stack.shape[0]
        current_frame_idx = 0
        is_playing = False
        window_name = f'Channel {channel_idx}'
        cv2.namedWindow(window_name)
        def on_trackbar(val):
            nonlocal current_frame_idx
            current_frame_idx = val

        cv2.createTrackbar('Frame', window_name, 0, total_frames - 1, on_trackbar)

        while True:
            frame = channel_stack[current_frame_idx]
            norm_frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
            norm_frame = norm_frame.astype(np.uint8)
            cv2.imshow(window_name, norm_frame)

            key = cv2.waitKey(delay if is_playing else 0) & 0xFF

            if key == ord('q'):
                break
            elif key == ord(' '):
                is_playing = not is_playing
            elif key == 81:  # Left arrow
                current_frame_idx = max(0, current_frame_idx - 1)
            elif key == 83:  # Right arrow
                current_frame_idx = min(total_frames - 1, current_frame_idx + 1)

            if is_playing:
                current_frame_idx = (current_frame_idx + 1) % total_frames
                cv2.setTrackbarPos('Frame', window_name, current_frame_idx)
            else:
                cv2.setTrackbarPos('Frame', window_name, current_frame_idx)
        cv2.destroyAllWindows()

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

    def optical_flow(self, channel_idx : int,
                     pyr_scale : float = 0.5, 
                     levels : int = 3, 
                     winsize : int = 15,
                     iterations : int = 3, 
                     poly_n : int = 5, 
                     poly_sigma : float = 1.2,
                     flag : int = 0, 
                     **kwargs):
        """
        Computes dense optical flow using Farneback method on a preprocessed channel.

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