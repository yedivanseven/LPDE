from multiprocessing import Array, Queue
from numpy import float64

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class SmootherParams():
    def __init__(self, control: QUEUE, coefficients: QUEUE,
                 smoothed: ARRAY, decay: float =1.0) -> None:
        self.__control = self.__queue_type_checked(control)
        self.__coefficients = self.__queue_type_checked(coefficients)
        self.__smoothed = self.__array_type_checked(smoothed)
        self.__decay = self.__float_type_and_range_checked(decay)

    @property
    def control(self) -> QUEUE:
        return self.__control

    @property
    def coefficients(self) -> QUEUE:
        return self.__coefficients

    @property
    def smoothed(self) -> ARRAY:
        return self.__smoothed

    @property
    def decay(self) -> float:
        return self.__decay

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError('Coefficients must be a multiprocessing Queue!')
        return value

    @staticmethod
    def __array_type_checked(value: ARRAY) -> ARRAY:
        if not type(value) is ARRAY:
            raise TypeError('Smoothed must be a multiprocessing Array!')
        return value

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if not type(value) in (int, float, float64):
            raise TypeError('Decay constant must be a number!')
        if value <= 0:
            raise ValueError('Decay constant must be positive !')
        return value
