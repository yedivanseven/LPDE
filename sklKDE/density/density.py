from multiprocessing import Manager
from numpy import exp, frombuffer, ndarray
from numpy import linspace, meshgrid, column_stack               # Remove line!
from sklearn.neighbors import KernelDensity
from .controller import Controller
from .parameters import DensityParams, ControllerParams, KDE_PARAMETERS
from ..geometry import PointAt


class Density:
    def __init__(self, params: DensityParams) -> None:
        self.__params = self.__params_type_checked(params)
        self.__data = Manager().dict()
        controller_params = ControllerParams(self.__params, self.__data)
        self.__controller = Controller(controller_params)
        self.__density = frombuffer(self.__controller.gridmap.output.get_obj())
        self.__kde = KernelDensity(bandwidth=self.__params.kernel.bandwidth,
                                   kernel=self.__params.kernel.name,
                                   **KDE_PARAMETERS)
        self.__grid = self.__grid_from_params()                  # Remove line!

    @property
    def controller(self) -> Controller:
        return self.__controller

    @property
    def on_grid(self) -> ndarray:
        return self.__density.reshape(self.__params.grid.shape)

    def at(self, point: PointAt) -> float:
        if self.__data:
            point = self.__point_type_and_range_checked(point)
            n_points = len(self.__data)
            self.__kde.fit(self.__data.values())
            density = exp(self.__kde.score_samples(point.position[None]))
            return float(n_points * density)

    def compute_on_grid(self) -> ndarray:                        # Remove line!
        if self.__data:                                          # Remove line!
            n_points = len(self.__data)                          # Remove line!
            self.__kde.fit(self.__data.values())                 # Remove line!
            density_on_grid = exp(self.__kde.score_samples(self.__grid))  #
            return n_points * density_on_grid.reshape(self.__params.grid.shape)

    @staticmethod
    def __params_type_checked(value: DensityParams) -> DensityParams:
        if type(value) is not DensityParams:
            raise TypeError('Parameters must be of type <DensityParams>!')
        return value

    def __point_type_and_range_checked(self, value: PointAt) -> PointAt:
        if type(value) is not PointAt:
            raise TypeError('Data point must be of type <PointAt>!')
        if not self.__params.bounds.contain(value):
            raise ValueError('Data point lies outside bounding box!')
        return value

    def __grid_from_params(self) -> ndarray:                     # Remove line!
        x_line = linspace(*self.__params.bounds.x_range, self.__params.grid.x)
        y_line = linspace(*self.__params.bounds.y_range, self.__params.grid.y)
        x_grid, y_grid = meshgrid(x_line, y_line)                # Remove line!
        return column_stack((x_grid.ravel(), y_grid.ravel()))    # Remove line!
