from numpy import ndarray
from matplotlib.figure import Figure
from matplotlib.pyplot import subplots, colorbar
from matplotlib.animation import FuncAnimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .helpers.typechecks import numpy_array_type_checked
from .helpers.typechecks import boundingbox_type_checked
from ..geometry import BoundingBox

DEFAULT_FIGURE_SIZE_IN_X: float = 8.0


def basic(data: ndarray, bounds: BoundingBox) -> None:
    data = numpy_array_type_checked(data)
    bounds = boundingbox_type_checked(bounds)

    fig_size_x = DEFAULT_FIGURE_SIZE_IN_X

    fig, ax = subplots(figsize=(fig_size_x, fig_size_x*bounds.aspect))
    fig.tight_layout()
    axlabel = ax.set(xlabel='longitude', ylabel='latitude')
    divider = make_axes_locatable(ax)
    contour = ax.imshow(data,
                        cmap='viridis',
                        extent=bounds.x_range+bounds.y_range,
                        origin='lower',
                        animated=True)
    cbax = divider.append_axes('right', size='5%', pad=0.1)
    cbar = colorbar(contour, cax=cbax, label='demand')

    def update_figure(*args):
        contour.set_data(data)
        contour.set_clim(data.min(), data.max())
        return contour,

    animation = FuncAnimation(fig, update_figure, interval=50, blit=False)
    fig.show()
