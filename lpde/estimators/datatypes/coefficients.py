from numpy import zeros, ndarray
from .degree import Degree


class Coefficients:
    def __init__(self, degree: Degree) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__size = (self.__degree.k_max + 1) * (self.__degree.l_max + 1)
        self.__shape = (self.__degree.k_max + 1, self.__degree.l_max + 1)
        self.__vector = zeros(self.__size)
        self.__vector[0] = 1.0

    @property
    def vec(self) -> ndarray:
        return self.__vector

    @vec.setter
    def vec(self, vector: ndarray) -> None:
        self.__vector = self.__vector_type_and_dim_checked(vector)

    @property
    def mat(self) -> ndarray:
        return self.__vector.reshape(self.__shape)

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if type(value) is not Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    def __vector_type_and_dim_checked(self, value: ndarray) -> ndarray:
        if type(value) is not ndarray:
            raise TypeError('Coefficient vector must be a numpy array!')
        if len(value.shape) != 1:
            raise ValueError('Coefficient vector must be 1-dimensional!')
        if value.size != self.__size:
            raise ValueError(f'Coefficient vector not of size {self.__size}!')
        return value


if __name__ == '__main__':
    degree = Degree(5, 5)
    coefficients = Coefficients(degree)
    print(coefficients.vec)
    print(coefficients.mat)
