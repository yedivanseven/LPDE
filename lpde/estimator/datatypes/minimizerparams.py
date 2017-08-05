from multiprocessing import Array, Queue
from .degree import Degree

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class MinimizerParams:
    def __init__(self, degree: Degree, control: QUEUE,
                 phi_queue: QUEUE, coeff_queue: QUEUE) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__control = self.__queue_type_checked(control)
        self.__phi_queue = self.__queue_type_checked(phi_queue)
        self.__coeff_queue = self.__queue_type_checked(coeff_queue)

    @property
    def degree(self):
        return self.__degree

    @property
    def control(self):
        return self.__control

    @property
    def phi_queue(self):
        return self.__phi_queue

    @property
    def coeff_queue(self):
        return self.__coeff_queue

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError('Control, coefficients, and phi must be Queues!')
        return value
