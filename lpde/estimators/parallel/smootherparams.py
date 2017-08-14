from multiprocessing import Array, Queue
from numpy import float64

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class SmootherParams():
    def __init__(self, control_queue: QUEUE, coeff_queue: QUEUE,
                 smoothed: ARRAY, decay) -> None:
        self.__control_queue = self.__queue_type_checked(control_queue)
        self.__coeff_queue = self.__queue_type_checked(coeff_queue)
        self.__smooth_coeffs = self.__array_type_checked(smoothed)
        self.__decay = self.__float_type_and_range_checked(decay)

    @property
    def control_queue(self) -> QUEUE:
        return self.__control_queue

    @property
    def coeff_queue(self) -> QUEUE:
        return self.__coeff_queue

    @property
    def smooth_coeffs(self) -> ARRAY:
        return self.__smooth_coeffs

    @property
    def decay(self) -> float:
        return self.__decay

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError('Control and coefficients must be Queues!')
        return value

    @staticmethod
    def __array_type_checked(value: ARRAY) -> ARRAY:
        if not type(value) is ARRAY:
            raise TypeError('Smooth coefficients must be a shared Array!')
        return value

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if not type(value) in (int, float, float64):
            raise TypeError('Decay constant must be a number!')
        if value <= 0:
            raise ValueError('Decay constant must be positive !')
        return value
