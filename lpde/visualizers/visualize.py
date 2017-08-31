from matplotlib.pyplot import figure, axes, colorbar, close
from matplotlib.image import AxesImage
from matplotlib.animation import FuncAnimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .colormaps import transparent_viridis
from ..estimators import ParallelEstimator
try:
    from cartopy.io.img_tiles import OSM
except ImportError:
    CARTOPY_WORKS = False
else: CARTOPY_WORKS = True

DEFAULT_FIGURE_SIZE_IN_X: float = 10.0
DEFAULT_UPDATE_INTERVAL: int = 100
AXIS_TYPE = type(axes())
close()


class Visualize:
    def __init__(self, density: ParallelEstimator) -> None:
        self.__density = self.__density_type_checked(density)
        self.__image = None
        self.__extent = self.__density.bounds.x_range + \
                        self.__density.bounds.y_range

    def show(self, cartopy: bool =False) -> FuncAnimation:
        we_use_cartopy = self.__boolean_type_checked(cartopy)
        figure_size = (DEFAULT_FIGURE_SIZE_IN_X,
                       DEFAULT_FIGURE_SIZE_IN_X * self.__density.bounds.aspect)
        image_figure = figure(figsize=figure_size)
        if we_use_cartopy:
            osm = OSM()
            contour_axis = axes(projection=osm.crs)
            contour_axis.set_extent(self.__extent)
            contour_axis.add_image(osm, 10)
            image_extent = contour_axis.get_extent()
            colormap = transparent_viridis()
        else:
            contour_axis = axes()
            image_extent = self.__extent
            colormap = 'viridis'
        ax_xy_labels = contour_axis.set(xlabel='longitude', ylabel='latitude')
        self.__image = contour_axis.imshow(self.__density.on_grid,
                                           cmap=colormap,
                                           extent=image_extent,
                                           origin='lower',
                                           animated=True)
        if not we_use_cartopy:
            self.__add_colorbar_to(contour_axis)
        animation = FuncAnimation(image_figure,
                                  self.__update,
                                  init_func=self.__initialize,
                                  interval=DEFAULT_UPDATE_INTERVAL,
                                  blit=we_use_cartopy)
        image_figure.tight_layout()
        image_figure.show()
        return animation

    def __add_colorbar_to(self, axis: AXIS_TYPE) -> None:
        axis_locs = make_axes_locatable(axis)
        cbar_axis = axis_locs.append_axes('right', size='5%', pad=0.1)
        cbar_plot = colorbar(self.__image, cax=cbar_axis, label='density')

    def __initialize(self) -> (AxesImage,):
        return self.__image,

    def __update(self, _) -> (AxesImage,):
        image_data = self.__density.on_grid
        self.__image.set_data(image_data)
        self.__image.set_clim(image_data.min(), image_data.max())
        return self.__image,

    @staticmethod
    def __density_type_checked(value: ParallelEstimator) -> ParallelEstimator:
        if type(value) is not ParallelEstimator:
            raise TypeError('Density must be of type <ParallelEstimator>!')
        return value

    @staticmethod
    def __boolean_type_checked(value: bool) -> bool:
        if type(value) is not bool:
            raise TypeError('Cartopy flag must be boolean!')
        if not CARTOPY_WORKS:
            return not value
        return value
