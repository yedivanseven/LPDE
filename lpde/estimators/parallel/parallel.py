from numpy import square, ndarray, float64, frombuffer, linspace, meshgrid
from numpy.polynomial.legendre import legvander2d, legval2d
from pandas import DataFrame
from .controller import Controller
from ...geometry import Mapper, PointAt, Grid
from ..datatypes import Coefficients, Scalings, Event, Degree, Action


class ParallelEstimator:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__c = Coefficients(self.__degree)
        self.__scale = Scalings(self.__degree)
        self.__controller = Controller(self.__degree, self.__map)
        self.__c.vec = frombuffer(self.__controller.smooth_coeffs.get_obj())

    @property
    def controller(self) -> Controller:
        return self.__controller

    def at(self, point: PointAt) -> float64:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        p = square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))
        return self.__map.out(p * float64(self.__controller.N))

    def on(self, grid: Grid) -> ndarray:
        grid = self.__grid_type_checked(grid)
        x_line = linspace(*self.__map.legendre_interval, grid.x)
        y_line = linspace(*self.__map.legendre_interval, grid.y)
        x_grid, y_grid = meshgrid(x_line, y_line)
        p = square(legval2d(x_grid, y_grid, self.__c.mat/self.__scale.mat))
        return p * float64(self.__controller.N)

    def update_with(self, event: Event) -> None:
        event = self.__event_type_checked(event)
        try:
            self.__controller.event_queue.put(event)
        except AssertionError:
            raise AssertionError('Event queue is already closed. Instantiate a'
                                 ' new <Parallel> object to get going again!')
    @property
    def _c(self) -> ndarray:
        return self.__c.vec

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __mapper_type_checked(value: Mapper) -> Mapper:
        if not type(value) is Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return value

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if not type(value) is PointAt:
            raise TypeError('Point must be of type <PointAt>!')
        return value

    @staticmethod
    def __event_type_checked(value: Event) -> Event:
        if not type(value) is Event:
            raise TypeError('Event must be of type <Event>!')
        return value

    @staticmethod
    def __grid_type_checked(value: Grid) -> Grid:
        if not type(value) is Grid:
            raise TypeError('Grid must be of type <Grid>!')
        return value
