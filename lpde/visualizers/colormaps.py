from matplotlib.pyplot import cm
from matplotlib.colors import ListedColormap
from numpy import arange, linspace


def transparent_viridis():
    original_colormap = cm.viridis
    modified_colormap = original_colormap(arange(original_colormap.N))
    modified_colormap[:, -1] = linspace(0, 1, original_colormap.N)
    return ListedColormap(modified_colormap)