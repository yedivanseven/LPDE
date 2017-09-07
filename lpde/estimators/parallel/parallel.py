from typing import Union
from numpy import square, ndarray, dtype, frombuffer, linspace, meshgrid
from numpy.polynomial.legendre import legval2d, legder
from .controller import Controller
from ..datatypes import Coefficients, Scalings, Event, Degree
from ...geometry import Mapper, PointAt, Grid, BoundingBox
from ...producers import MockParams

DEFAULT_PIXELS_Y: int = 100
NUMPY_TYPE = Union[dtype, ndarray]


class ParallelEstimator:
    def __init__(self, degree: Degree, mapper: Mapper,
                 producer_params: MockParams) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        params = self.__producer_params_type_checked(producer_params)
        self.__controller = Controller(self.__degree, self.__map, params)
        self.__c = Coefficients(self.__degree)
        self.__c.vec = frombuffer(self.__controller.smooth_coeffs.get_obj())
        self.__scale = Scalings(self.__degree)
        pixels_x = int(DEFAULT_PIXELS_Y / self.__map.bounds.aspect)
        self.__grid = self.__make(Grid(pixels_x, DEFAULT_PIXELS_Y))

    @property
    def bounds(self) -> BoundingBox:
        return self.__map.bounds

    @property
    def controller(self) -> Controller:
        return self.__controller

    @property
    def grid(self) -> (ndarray, ndarray):
        return self.__grid

    @grid.setter
    def grid(self, grid: Grid) -> None:
        grid = self.__grid_type_checked(grid)
        self.__grid = self.__make(grid)

    @property
    def on_grid(self) -> ndarray:
        return self.__density(self.__grid)

    @property
    def gradient_on_grid(self) -> (ndarray, ndarray):
        return self.__gradient(self.__grid)

    def at(self, point: PointAt) -> dtype:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        return self.__density(mapped_point)

    def gradient_at(self, point: PointAt) -> (dtype, dtype):
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        return self.__gradient(mapped_point)

    def update_with(self, event: Event) -> None:
        event = self.__event_type_checked(event)
        try:
            self.__controller.event_queue.put(event)
        except AssertionError:
            raise AssertionError('Event queue is already closed. Instantiate a'
                                 ' new <Parallel> object to get going again!')

    def __make(self, grid: Grid) -> (ndarray, ndarray):
        x_line = linspace(*self.__map.legendre_interval, grid.x)
        y_line = linspace(*self.__map.legendre_interval, grid.y)
        return meshgrid(x_line, y_line)

    def __density(self, point_grid: NUMPY_TYPE) -> NUMPY_TYPE:
        density = square(legval2d(*point_grid, self.__c.mat/self.__scale.mat))
        return self.__map.out(density) * self.__controller.N

    def __gradient(self, point_grid: ndarray) -> (NUMPY_TYPE, NUMPY_TYPE):
        coeffs_of_grad_x = legder(self.__c.mat / self.__scale.mat, axis=0)
        coeffs_of_grad_y = legder(self.__c.mat / self.__scale.mat, axis=1)
        sqrt_p = legval2d(*point_grid, self.__c.mat/self.__scale.mat)
        factor = 2.0 * self.__controller.N
        grad_x = factor * sqrt_p * legval2d(*point_grid, coeffs_of_grad_x)
        grad_y = factor * sqrt_p * legval2d(*point_grid, coeffs_of_grad_y)
        return self.__map.out(grad_x), self.__map.out(grad_y)

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if type(value) is not Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __mapper_type_checked(value: Mapper) -> Mapper:
        if type(value) is not Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return value

    @staticmethod
    def __producer_params_type_checked(value: MockParams) -> MockParams:
        if type(value) is not MockParams:
            raise TypeError('Type of parameters must be <ProducerParams>!')
        return value

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if type(value) is not PointAt:
            raise TypeError('Point must be of type <PointAt>!')
        return value

    @staticmethod
    def __event_type_checked(value: Event) -> Event:
        if type(value) is not Event:
            raise TypeError('Event must be of type <Event>!')
        return value

    @staticmethod
    def __grid_type_checked(value: Grid) -> Grid:
        if type(value) is not Grid:
            raise TypeError('Grid must be of type <Grid>!')
        return value
