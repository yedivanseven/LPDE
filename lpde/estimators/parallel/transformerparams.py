from multiprocessing import Queue
from ..datatypes import Degree
from ...geometry import Mapper

QUEUE = type(Queue())


class TransformerParams:
    def __init__(self, degree: Degree, mapper: Mapper,
                 event_queue: QUEUE, phi_queue: QUEUE) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__event_queue = self.__queue_type_checked(event_queue)
        self.__phi_queue = self.__queue_type_checked(phi_queue)

    @property
    def degree(self) -> Degree:
        return self.__degree

    @property
    def map(self) -> Mapper:
        return self.__map

    @property
    def event_queue(self) -> QUEUE:
        return self.__event_queue

    @property
    def phi_queue(self) -> QUEUE:
        return self.__phi_queue

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __mapper_type_checked(value: Mapper) -> Mapper:
        if not type(value) is Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError(
                    'Control, event, and phi must be multiprocessing Queues!')
        return value
