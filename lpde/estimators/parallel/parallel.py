from numpy import square, ndarray, float64, frombuffer, linspace, meshgrid
from numpy.polynomial.legendre import legvander2d, legval2d
from pandas import DataFrame
from .estimator import Estimator
from ...geometry import Mapper, PointAt, Grid
from ..datatypes import Coefficients, Scalings, Event, Degree, Action


class Parallel:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__c = Coefficients(self.__degree)
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__c.mat.size))
        self.__N = 0
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}
        self.__estimator = Estimator(self.__degree)
        self.__phi_queue = self.__estimator.phi_queue
        self.__c.vec = frombuffer(self.__estimator.smooth_coeffs.get_obj())

    @property
    def estimator(self) -> Estimator:
        return self.__estimator

    def at(self, point: PointAt) -> float64:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        p = square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))
        return self.__map.out(p * float64(self.__N))

    def on(self, grid: Grid) -> ndarray:
        grid = self.__grid_type_checked(grid)
        x_line = linspace(*self.__map.legendre_interval, grid.x)
        y_line = linspace(*self.__map.legendre_interval, grid.y)
        x_grid, y_grid = meshgrid(x_line, y_line)
        return square(legval2d(x_grid, y_grid, self.__c.mat/self.__scale.mat))

    def update_with(self, event: Event) -> None:
        event = self.__event_type_checked(event)
        data_changed_due_to = self.__handler_of[event.action]
        if data_changed_due_to(event):
            try:
                self.__phi_queue.put(self.__phi_ijn.values)
            except AssertionError:
                err_msg = ('Phi queue is already closed. Instantiate a'
                           ' new <Parallel> object to get going again!')
                raise AssertionError(err_msg)

    def __add(self, event: Event) -> bool:
        if event.id not in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            self.__N += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            self.__phi_ijn.drop(event.id, axis=1, inplace=True)
            self.__N -= 1
            return True
        return False

    @property
    def _phi_queue_empty(self) -> bool:
        return self.__phi_queue.empty()

    @property
    def _c(self) -> ndarray:
        return self.__c.vec

    @property
    def _phi(self) -> DataFrame:
        return self.__phi_ijn

    @property
    def _N(self) -> int:
        return self.__N

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
