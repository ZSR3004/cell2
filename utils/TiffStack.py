import tifffile as tiff
import numpy as np

class TiffStack():
    def __init__(self, path, nchannels = 3, dtype = np.uint16):
        self.path = path
        self.df = tiff.imread(path)
        assert self.df.shape[1] == nchannels, f"Expected {nchannels}, but got {self.df.shape[2]}"
        assert self.df.dtype == dtype, f"Expected {dtype}, but got {self.df.dtype}"
        self.img = tiff.TiffFile(path)