import imageio
import numpy as np
from datetime import datetime
from matplotlib import colors
import matplotlib.pyplot as plt

class Plotter():
    def __init__(self, **kwargs):
        self.SHOW_MAP = kwargs["plot_map"]
        self.Y_MIN = kwargs["y_min"]
        self.Y_MAX = kwargs["y_max"]

    