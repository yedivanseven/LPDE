from numpy import zeros, ndarray, float64
from .degree import Degree


class InitialCoefficients:
    def __init__(self, degree: Degree) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__size = (self.__degree.k_max + 1) * (self.__degree.l_max + 1) + 1
        self.__vector = zeros(self.__size)
        self.__vector[:2] = 1.0

    @property
    def vec(self) -> ndarray:
        return self.__vector

    @property
    def lagrange(self) -> float64:
        return self.__vector[0]

    @lagrange.setter
    def lagrange(self, value: int) -> None:
        self.__vector[0] = self.__integer_type_and_range_checked(value)

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Lagrange multiplier must be an integer!')
        if value < 0:
            raise ValueError('Lagrange multiplier must not be negative!')
        return value
