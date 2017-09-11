from multiprocessing import Process, Array
from multiprocessing import Event as Stop
from numpy import exp, linspace, meshgrid, column_stack, ndarray
from sklearn.neighbors import KernelDensity
from .parameters import GridMapperParams, KDE_PARAMETERS

ARRAY = type(Array('d', 10))


class GridMapper(Process):
    def __init__(self, params: GridMapperParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__stop = Stop()
        self.__output = Array('d', self.__params.grid.size)
        self.__kde = KernelDensity(bandwidth=self.__params.kernel.bandwidth,
                                   kernel=self.__params.kernel.name,
                                   **KDE_PARAMETERS)
        self.__grid = self.__grid_from_params()

    @property
    def stop(self):
        return self.__stop

    @property
    def output(self) -> ARRAY:
        return self.__output

    def run(self) -> None:
        while not self.__stop.is_set():
            if self.__params.data:
                n_points = len(self.__params.data)
                self.__kde.fit(self.__params.data.values())
                density_on_grid = exp(self.__kde.score_samples(self.__grid))
                with self.__output.get_lock():
                    self.__output.get_obj()[:] = n_points * density_on_grid

    def __grid_from_params(self) -> ndarray:
        x_line = linspace(*self.__params.bounds.x_range, self.__params.grid.x)
        y_line = linspace(*self.__params.bounds.y_range, self.__params.grid.y)
        x_grid, y_grid = meshgrid(x_line, y_line)
        return column_stack((x_grid.ravel(), y_grid.ravel()))

    @staticmethod
    def __params_type_checked(value: GridMapperParams) -> GridMapperParams:
        if type(value) is not GridMapperParams:
            raise TypeError('Parameters must be of type <GridMapperParams>!')
        return value
