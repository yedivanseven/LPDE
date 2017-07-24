from numpy import zeros, square, log, ndarray
from numpy.polynomial.legendre import legvander2d, legval2d
from scipy.optimize import fmin_l_bfgs_b, minimize
from pandas import DataFrame
from ..geometry import Mapper, PointAt
from .helpers import Coefficients, InitialCoefficients
from .helpers import Scalings, Event, Degree, Action

GRADIENT_TOLERANCE = 1.0
MAXIMUM_ITERATIONS = 10000


class DensityEstimate:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__type_checked(mapper)
        self.__c_init = InitialCoefficients(self.__degree)
        self.__c = Coefficients(self.__degree)
        self.__grad_c = zeros(self.__c.vec.size)
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__c.mat.size))
        self.__data_changed_due_to = {Action.ADD: self.__add,
                                      Action.MOVE: self.__move,
                                      Action.DELETE: self.__delete}
        self.__constraint = {'type': 'eq',
                             'fun': self.__norm,
                             'jac': self.__grad_norm}
        self.__options = {'maxiter': MAXIMUM_ITERATIONS,
                          'disp': False}
        self._number_of_fallbacks = 0
        self._number_of_failures = 0
        self.__N = 0

    def at(self, point: PointAt) -> ndarray:
        mapped_point = self.__map.in_from(point)
        return square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))

    def update_with(self, event: Event) -> None:
        if not self.__data_changed_due_to[event.action](event):
            return
        self.__c_init.lagrange = self.__N
        coefficients, _, status = fmin_l_bfgs_b(self.__lagrangian,
                                                self.__c_init.vec,
                                                self.__grad_lagrangian,
                                                **self.__options)
        if (status['warnflag'] == 0 and
                self.__grad_c.dot(self.__grad_c) < GRADIENT_TOLERANCE):
            self.__c.vec = coefficients
        else:
            result = minimize(self.__neg_log_l, self.__c_init.vec[1:],
                              method='slsqp',
                              jac=self.__grad_neg_log_l,
                              constraints=self.__constraint,
                              options=self.__options)
            if result.success:
                self.__c.vec[1:] = result.x
                self.__c.vec[0] = self.__N
                self._number_of_fallbacks += 1
            else:
                self._number_of_failures += 1

    def __add(self, event: Event) -> bool:
        if event.id not in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            self.__phi_ijn.loc[:, event.id] = \
                legvander2d(*location, self.__degree).T / self.__scale.vec
            self.__N += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            self.__phi_ijn.loc[:, event.id] = \
                legvander2d(*location, self.__degree).T / self.__scale.vec
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            self.__phi_ijn.drop(event.id, axis=1, inplace=True)
            self.__N -= 1
            return True
        return False

    def __lagrangian(self, c: ndarray) -> float:
        return -log(square(c[1:].dot(self.__phi_ijn))).sum() + \
               c[0] * (c[1:].dot(c[1:]) - 1.0)

    def __grad_lagrangian(self, c: ndarray) -> ndarray:
        self.__grad_c[0] = c[1:].dot(c[1:]) - 1.0
        self.__grad_c[1:] = -2.0*(self.__phi_ijn /
                c[1:].dot(self.__phi_ijn)).sum(axis=1) + 2.0*c[0]*c[1:]
        return self.__grad_c

    def __neg_log_l(self, c: ndarray) -> float:
        return -log(square(c.dot(self.__phi_ijn))).sum()

    def __grad_neg_log_l(self, c: ndarray) -> ndarray:
        return -2.0 * (self.__phi_ijn / c.dot(self.__phi_ijn)).sum(axis=1)

    def _on(self, x_grid: ndarray, y_grid: ndarray) -> ndarray:
        return square(legval2d(x_grid, y_grid, self.__c.mat/self.__scale.mat))

    @staticmethod
    def __norm(c: ndarray) -> float:
        return c.dot(c) - 1.0

    @staticmethod
    def __grad_norm(c: ndarray) -> ndarray:
        return 2.0 * c

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
    def __type_checked(mapper: Mapper) -> Mapper:
        if not type(mapper) is Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return mapper
