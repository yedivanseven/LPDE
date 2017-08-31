from matplotlib.pyplot import cm
from matplotlib.colors import ListedColormap
from numpy import arange, linspace


def transparent_viridis():
    mpl_cmap = cm.viridis
    new_cmap = mpl_cmap(arange(mpl_cmap.N))
    new_cmap[:, -1] = linspace(0, 1, mpl_cmap.N)
    return ListedColormap(new_cmap)