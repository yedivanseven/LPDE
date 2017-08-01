from multiprocessing import Array, Queue
from numpy import exp, float64

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class SmootherParams():
    def __init__(self, control: QUEUE, coefficients: QUEUE, smoothed: ARRAY,
                 decay: float =1.0, timestep: float =0.1) -> None:
        self.__control = self.__queue_type_checked(control)
        self.__coefficients = self.__queue_type_checked(coefficients)
        self.__smoothed = self.__array_type_checked(smoothed)
        self.__decay, self.__timestep = self.__checked(decay, timestep)
        self.__damp = 1.0 - exp(-self.__timestep / self.__decay)

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
    def timestep(self) -> float:
        return self.__timestep

    @property
    def damp(self) -> float:
        return self.__damp

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError('Coefficients must be a multiprocessing Queue!')
        return value

    @staticmethod
    def __array_type_checked(value: ARRAY) -> ARRAY:
        if not type(value) is ARRAY:
            raise TypeError('Smoothed must be multiprocessing Arrays!')
        return value

    @staticmethod
    def __checked(decay: float, timestep: float) -> (float, float):
        allowed_types = (int, float, float64)
        types_allowed = (type(decay) in allowed_types,
                         type(timestep) in allowed_types)
        if not all(types_allowed):
            raise TypeError('Decay and timestep must be numeric!')
        if not all((decay > 0, timestep > 0)):
            raise ValueError('Decay and timestep must > 0 !')
        return decay, timestep