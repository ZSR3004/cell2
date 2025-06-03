import cv2

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