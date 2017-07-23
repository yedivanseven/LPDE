from numpy import square, log, ndarray, float64
from numpy.polynomial.legendre import legvander2d, legval2d
from numpy.linalg import norm
from scipy.optimize import fmin_ncg
from pandas import DataFrame
from ..geometry import Mapper, PointAt
from .helpers import Coefficients, Scalings, Event, Degree, Action


class DensityEstimate:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__type_checked(mapper)
        self.__c = Coefficients(self.__degree)
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__c.vec.size))
        self.__data_changed_due_to = {Action.ADD: self.__add,
                                      Action.MOVE: self.__move,
                                      Action.DELETE: self.__delete}

    def at(self, point: PointAt) -> ndarray:
        mapped_point = self.__map.in_from(point)
        return square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))

    def update_with(self, event: Event) -> None:
        if self.__data_changed_due_to[event.action](event):
            self.__c.vec = fmin_ncg(self.__lagrangian,
                                    self.__c.vec,
                                    self.__gradient_lagrangian,
                                    disp=False)

    def __add(self, event: Event) -> bool:
        if event.id not in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            self.__phi_ijn.loc[:, event.id] = \
                legvander2d(*location, self.__degree).T / self.__scale.vec
            return True
        else:
            return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            self.__phi_ijn.loc[:, event.id] = \
                legvander2d(*location, self.__degree).T / self.__scale.vec
            return True
        else:
            return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            self.__phi_ijn.drop(event.id, axis=1, inplace=True)
            return True
        else:
            return False

    def __lagrangian(self, c: ndarray) -> float:
        sqrt_p = c.dot(self.__phi_ijn)
        return -log(square(sqrt_p)).sum() + \
                norm((self.__phi_ijn / sqrt_p).sum(axis=1)) * (c.dot(c) - 1)

    def __gradient_lagrangian(self, c: ndarray) -> ndarray:
        sigma = (self.__phi_ijn / c.dot(self.__phi_ijn)).sum(axis=1).values
        return -2*sigma + 2*norm(sigma)*c

    def _on(self, x_grid: ndarray, y_grid: ndarray) -> ndarray:
        phi = legvander2d(x_grid, y_grid, self.__degree).T / self.__scale.vec
        return square(self.__c.vec.dot(phi)).reshape((50, 50))

    @property
    def _c(self) -> ndarray:
        return self.__c.vec

    @property
    def _phi(self) -> DataFrame:
        return self.__phi_ijn

    @staticmethod
    def __normalization(c: ndarray) -> float64:
        return c.dot(c) - float64(1.0)

    @staticmethod
    def __gradient_normalization(c: ndarray) -> ndarray:
        return 2*c

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __type_checked(mapper: Mapper) -> Mapper:
        if not type(mapper) is Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return mapper
