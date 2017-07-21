from numpy import ndarray, zeros


class Coefficients:
    def __init__(self, k_max: int, l_max: int) -> None:
        self.__k_max = self.__type_and_range_checked(k_max)
        self.__l_max = self.__type_and_range_checked(l_max)
        self.__size = self.__k_max * self.__l_max
        self.__shape = (self.__k_max, self.__l_max)
        self.__vector = zeros(self.__size)
        self.__vector[0] = 1
        self.__matrix = self.__vector.reshape(self.__shape)

    @property
    def vec(self) -> ndarray:
        return self.__vector

    @vec.setter
    def vec(self, vector: ndarray) -> None:
        self.__vector = self.__vector_type_and_dim_checked(vector)
        self.__matrix = self.__vector.reshape(self.__shape)

    @property
    def mat(self) -> ndarray:
        return self.__matrix

    @mat.setter
    def mat(self, matrix: ndarray) -> None:
        self.__matrix = self.__matrix_type_and_dim_checked(matrix)
        self.__vector = self.__matrix.ravel()

    @staticmethod
    def __type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Maximum polynomial degree must be an integer!')
        if value < 0:
            raise ValueError('Maximum polynomial degree must not be negative!')
        return value

    def __vector_type_and_dim_checked(self, vector: ndarray) -> ndarray:
        if not type(vector) is ndarray:
            raise TypeError('Coefficient vector must be a numpy array!')
        if len(vector.shape) != 1:
            raise ValueError('Coefficient vector must be 1-dimensional!')
        if vector.size != self.__size:
            raise ValueError(f'Coeff. vector should be of size {self.__size}!')
        return vector

    def __matrix_type_and_dim_checked(self, matrix: ndarray) -> ndarray:
        if not type(matrix) is ndarray:
            raise TypeError('Coefficient matrix must be a numpy array!')
        if len(matrix.shape) != 2:
            raise ValueError('Coefficient matrix must be 2-dimensional!')
        if matrix.shape != self.__shape:
            raise ValueError('Coefficient matrix is of wrong size!')
        return matrix
