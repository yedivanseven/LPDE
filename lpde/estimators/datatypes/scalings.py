from numpy import sqrt, array, ndarray, newaxis
from .degree import Degree


class Scalings:
    def __init__(self, degree: Degree) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__matrix = array([[2 / sqrt((2*k + 1)*(2*l + 1))
                                for l in range(self.__degree.l_max + 1)]
                               for k in range(self.__degree.k_max + 1)])
        self.__vector = self.__matrix.ravel()
        self.__vector_transposed = self.__vector[:, newaxis]

    @property
    def vec(self) -> ndarray:
        return self.__vector

    @property
    def vecT(self) -> ndarray:
        return self.__vector_transposed

    @property
    def mat(self) -> ndarray:
        return self.__matrix

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if type(value) is not Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value


if __name__ == '__main__':
    degree = Degree(5, 5)
    scale = Scalings(degree)
    print(scale.mat)
    print(scale.vec)
    print(scale.vecT)
