from typing import Union
from numpy import square, ndarray, dtype, frombuffer, linspace, meshgrid, array
from numpy.polynomial.legendre import legval2d, legder
from .controller import Controller
from ..datatypes import Coefficients, Scalings, Event, Degree
from ...geometry import Mapper, PointAt, Grid, BoundingBox
from ...producers import MockParams

DEFAULT_PIXELS_Y: int = 100


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
        p = square(legval2d(*self.__grid, self.__c.mat/self.__scale.mat))
        return self.__map.out(p) * self.__controller.N

    @property
    def gradient_on_grid(self) -> (ndarray, ndarray):
        coeffs_of_grad_x = legder(self.__c.mat/self.__scale.mat, axis=0)
        coeffs_of_grad_y = legder(self.__c.mat/self.__scale.mat, axis=1)
        grad_x = (legval2d(*self.__grid, self.__c.mat/self.__scale.mat) *
                  legval2d(*self.__grid, coeffs_of_grad_x) * 2.0)
        grad_y = (legval2d(*self.__grid, self.__c.mat/self.__scale.mat) *
                  legval2d(*self.__grid, coeffs_of_grad_y) * 2.0)
        return (self.__map.out(grad_x) * self.__controller.N,
                self.__map.out(grad_y) * self.__controller.N)

    def at(self, point: PointAt) -> Union[dtype, ndarray]:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        p = square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))
        return self.__map.out(p) * self.__controller.N

    def gradient_at(self, point: PointAt) -> ndarray:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        coeffs_of_grad_x = legder(self.__c.mat/self.__scale.mat, axis=0)
        coeffs_of_grad_y = legder(self.__c.mat/self.__scale.mat, axis=1)
        grad_x = (legval2d(*mapped_point, self.__c.mat/self.__scale.mat) *
                  legval2d(*mapped_point, coeffs_of_grad_x) * 2.0)
        grad_y = (legval2d(*mapped_point, self.__c.mat/self.__scale.mat) *
                  legval2d(*mapped_point, coeffs_of_grad_y) * 2.0)
        print(mapped_point)
        print(grad_x)
        grad = array([grad_x, grad_y])
        return self.__map.out(grad) * self.__controller.N


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
