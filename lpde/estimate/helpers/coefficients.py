from numpy import zeros, ndarray
from .degree import Degree


class Coefficients:
    def __init__(self, degree: Degree) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__size = (self.__degree.k_max + 1) * (self.__degree.l_max + 1) + 1
        self.__shape = (self.__degree.k_max + 1, self.__degree.l_max + 1)
        self.__vector = zeros(self.__size)
        self.__vector[:2] = 1.0

    @property
    def size(self) -> int:
        return self.__size

    @property
    def vec(self) -> ndarray:
        return self.__vector[1:]

    @vec.setter
    def vec(self, vector: ndarray) -> None:
        self.__vector = self.__vector_type_and_dim_checked(vector)

    @property
    def mat(self) -> ndarray:
        return self.__vector[1:].reshape(self.__shape)

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    def __vector_type_and_dim_checked(self, value: ndarray) -> ndarray:
        if not type(value) is ndarray:
            raise TypeError('Coefficient vector must be a numpy array!')
        if len(value.shape) != 1:
            raise ValueError('Coefficient vector must be 1-dimensional!')
        if value.size != self.__size:
            raise ValueError(f'Coeff. vector should be of size {self.__size}!')
        return value
