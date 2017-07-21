from numpy import sqrt, array, newaxis, ndarray


class Scalings:
    def __init__(self, k_max: int, l_max: int) -> None:
        self.__k_max = self.__type_and_range_checked(k_max)
        self.__l_max = self.__type_and_range_checked(l_max)
        self.__matrix = array([[2 / sqrt((2*k + 1)*(2*l + 1))
                                for l in range(l_max)]
                               for k in range(k_max)])
        self.__vector = self.__matrix.ravel()[:, newaxis]

    @property
    def vec(self) -> ndarray:
        return self.__vector

    @property
    def mat(self) -> ndarray:
        return self.__matrix

    @staticmethod
    def __type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Maximum polynomial degree must be an integer!')
        if value < 0:
            raise ValueError('Maximum polynomial degree must not be negative!')
        return value
