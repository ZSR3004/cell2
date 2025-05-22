import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cv2

class TiffStack():
    def __init__(self, path, n_channels = 3, dtype = np.uint16):
        self.path = path
        self.df = tiff.imread(path)
        assert self.df.shape[1] == n_channels, f"Expected {n_channels}, but got {self.df.shape[2]}"
        assert self.df.dtype == dtype, f"Expected {dtype}, but got {self.df.dtype}"
        self.img = tiff.TiffFile(path)
    
    def isolate_channel(self, channel_idx):
        """
        Isolates a specific channel from the TIFF stack.

        Args:
            channel_idx (int): Index of the channel to isolate (0-indexed).

        Returns:
            np.ndarray: Isolated channel as a 3D numpy array.
        """
        assert 0 <= channel_idx < self.df.shape[1], f"Channel index out of range: {channel_idx}"
        return self.df[:, channel_idx, ...]

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
        assert 0 <= channel_idx < self.df.shape[1], f"Channel index out of range: {channel_idx}"
        channel_stack = self.df[:, channel_idx, ...]
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