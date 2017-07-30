from numpy import zeros, square, log, ndarray, float64
from numpy.polynomial.legendre import legvander2d, legval2d
from scipy.optimize import fmin_l_bfgs_b, minimize
from pandas import DataFrame
from ..geometry import Mapper, PointAt
from .datatypes import Coefficients, InitialCoefficients
from .datatypes import Scalings, Event, Degree, Action

GRADIENT_TOLERANCE = 0.1
MAXIMUM_ITERATIONS = 10000


class SerialEstimate:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__c_init = InitialCoefficients(self.__degree)
        self.__c = Coefficients(self.__degree)
        self.__grad_c = zeros(self.__c_init.vector.size)
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__c.mat.size))
        self.__handler_of = {Action.ADD: self.__add,
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

    def at(self, point: PointAt) -> float64:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        p = square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))
        return self.__map.out(p)

    def update_with(self, event: Event) -> None:
        event = self.__event_type_checked(event)
        data_changed_due_to = self.__handler_of[event.action]
        if not data_changed_due_to(event):
            return
        self.__c_init.lagrange = self.__N
        coefficients, _, status = fmin_l_bfgs_b(self.__lagrangian,
                                                self.__c_init.vector,
                                                self.__grad_lagrangian,
                                                **self.__options)
        converged = self.__grad_c.dot(self.__grad_c) < GRADIENT_TOLERANCE
        if (status['warnflag'] == 0) and converged:
            self.__c.vec = coefficients[1:]
        else:
            result = minimize(self.__neg_log_l, self.__c_init.coeffs,
                              method='slsqp',
                              jac=self.__grad_neg_log_l,
                              constraints=self.__constraint,
                              options=self.__options)
            if result.success:
                self.__c.vec = result.x
                self._number_of_fallbacks += 1
            else:
                self._number_of_failures += 1

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

    def __lagrangian(self, c: ndarray) -> float64:
        return self.__neg_log_l(c[1:]) + c[0]*self.__norm(c[1:])

    def __grad_lagrangian(self, c: ndarray) -> ndarray:
        self.__grad_c[0] = self.__norm(c[1:])
        self.__grad_c[1:] = self.__grad_neg_log_l(c[1:]) + 2.0*c[0]*c[1:]
        return self.__grad_c

    def __neg_log_l(self, c: ndarray) -> float64:
        return -log(square(c.dot(self.__phi_ijn.values))).sum()

    def __grad_neg_log_l(self, c: ndarray) -> ndarray:
        return float64(-2.0) * (self.__phi_ijn.values /
               c.dot(self.__phi_ijn.values)).sum(axis=1)

    @staticmethod
    def __norm(c: ndarray) -> float64:
        return c.dot(c) - float64(1.0)

    @staticmethod
    def __grad_norm(c: ndarray) -> ndarray:
        return 2.0 * c

    def _on(self, x_grid: ndarray, y_grid: ndarray) -> ndarray:
        return square(legval2d(x_grid, y_grid, self.__c.mat/self.__scale.mat))

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
