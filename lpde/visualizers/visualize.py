from matplotlib.pyplot import figure, axes, colorbar
from matplotlib.image import AxesImage
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Subplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.crs import PlateCarree
from cartopy.io.img_tiles import OSM
from cartopy.mpl.geoaxes import GeoAxesSubplot
from .colormaps import transparent_viridis
from ..estimators import ParallelEstimator

DEFAULT_FIGURE_SIZE_IN_X: float = 10.0
DEFAULT_UPDATE_INTERVAL: int = 100


class Visualize:
    def __init__(self, density: ParallelEstimator) -> None:
        self.__density = self.__density_type_checked(density)
        self.__image = None
        self.__depending_on_whether_we = {True: self.__cartopy_geo_axis,
                                          False: self.__matplotlib_axis}

    def show(self, cartopy: bool =False) -> FuncAnimation:
        use_cartopy = self.__boolean_type_checked(cartopy)
        figure_size = (DEFAULT_FIGURE_SIZE_IN_X,
                       DEFAULT_FIGURE_SIZE_IN_X * self.__density.bounds.aspect)
        image_figure = figure(figsize=figure_size)
        contour_axis, params = self.__depending_on_whether_we[use_cartopy]()
        self.__image = contour_axis.imshow(self.__density.on_grid,
                                           origin='lower',
                                           animated=True,
                                           extent=self.__density.bounds.extent,
                                           interpolation='bilinear',
                                           **params)
        if not use_cartopy:
            self.__add_colorbar_to(contour_axis)
        animation = FuncAnimation(image_figure,
                                  self.__update,
                                  init_func=self.__initialize,
                                  interval=DEFAULT_UPDATE_INTERVAL,
                                  blit=use_cartopy)
        image_figure.show()
        return animation

    def __cartopy_geo_axis(self) -> (GeoAxesSubplot, dict):
        osm = OSM()
        axis = axes(projection=osm.crs)
        axis.set_extent(self.__density.bounds.extent)
        axis.add_image(osm, 11)
        axis.text(-0.05, 0.50, 'latitude',
                  rotation='vertical',
                  verticalalignment='center',
                  transform=axis.transAxes)
        axis.text(0.5, -0.05, 'longitude',
                  rotation='horizontal',
                  horizontalalignment='center',
                  transform=axis.transAxes)
        plot_params = {'cmap': transparent_viridis(),
                       'transform': PlateCarree()}
        return axis, plot_params

    @staticmethod
    def __matplotlib_axis() -> (Subplot, dict):
        axis = axes()
        axis.set(xlabel='longitude', ylabel='latitude')
        plot_params = {'cmap': 'viridis'}
        return axis, plot_params

    def __add_colorbar_to(self, axis: Subplot) -> None:
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

    def __boolean_type_checked(self, value: bool) -> bool:
        if type(value) is not bool:
            raise TypeError('Cartopy flag must be boolean!')
        if value and not self.__density.bounds.are_geo:
            return False
        return value
