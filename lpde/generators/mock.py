from time import sleep
from random import randint, expovariate, sample
from uuid import uuid4
from multiprocessing import Process, Queue
from ..geometry import PointAt, BoundingBox
from ..estimators.datatypes import Action, Event

QUEUE = type(Queue())


class MockParams:
    def __init__(self, rate: float, build_up: int, n_events: int,
                 bounds: BoundingBox, dist: callable, event_queue: QUEUE):
        self.__rate = self.__float_type_and_range_checked(rate)
        self.__build_up = self.__integer_type_and_range_checked(build_up)
        self.__n_events = self.__integer_type_and_range_checked(n_events)
        self.__bounds = self.__bounds_type_checked(bounds)
        self.__dist = self.__function_type_checked(dist)
        self.__event_queue = self.__queue_type_checked(event_queue)

    @property
    def rate(self) -> float:
        return self.__rate

    @property
    def build_up(self) -> int:
        return self.__build_up

    @property
    def n_events(self) -> int:
        return self.__n_events

    @property
    def bounds(self) -> BoundingBox:
        return self.__bounds

    @property
    def dist(self) -> callable:
        return self.__dist

    @property
    def event_queue(self) -> QUEUE:
        return self.__event_queue

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if not type(value) is float:
            raise TypeError('Rate parameter must be a floating point number!')
        if value <= 0.0:
            raise ValueError('Rate parameter must be positive!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value) -> int:
        if not type(value) is int:
            raise TypeError('Build-up and number of events must be integers!')
        if value <= 0:
            raise ValueError('Build-up and number of events must be positive!')
        return value

    @staticmethod
    def __bounds_type_checked(value: BoundingBox) -> BoundingBox:
        if not type(value) is BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    def __function_type_checked(self, value: callable) -> callable:
        if not type(value) is function:
            raise TypeError('Distribution must be a callable function!')
        try:
            return_value = value(self.__bounds)
        except:
            raise RuntimeError('Call to distribution function failed!')
        if not type(return_value) is PointAt:
            raise TypeError('Return value of distribution must be <PointAt>!')
        if not self.__bounds.contain(return_value):
            raise ValueError('Returned point lies outside bounding box!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if not type(value) is QUEUE:
            raise TypeError('Event queue must be a multiprocessing Queue!')
        return value


class MockGenerator(Process):
    def __init__(self, params: MockParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__points = {}
        self.__according_to = {1: self.__add,
                               0: self.__move,
                              -1: self.__delete}

    def run(self) -> None:
        for _ in range(self.__params.build_up):
            event = self.__add()
            self.__push(event)
        for _ in range(self.__params.n_events):
            event_type = randint(-1, 1)
            event = self.__according_to[event_type]()
            self.__push(event)

    def __add(self) -> Event:
        location = self.__params.dist(self.__params.bounds)
        uuid = uuid4()
        self.__points[uuid] = location
        return Event(uuid, Action.ADD, location)

    def __move(self) -> Event:
        location = self.__params.dist(self.__params.bounds)
        uuid = sample(self.__points.keys())
        self.__points[uuid] = location
        return Event(uuid, Action.MOVE, location)

    def __delete(self) -> Event:
        uuid = sample(self.__points.keys())
        _ = self.__points.pop(uuid)
        return Event(uuid, Action.DELETE)

    def __push(self, event: Event) -> None:
        sleep(expovariate(self.__params.rate))
        try:
            self.__params.event_queue.put(event)
        except AssertionError:
            err_msg = ('Event queue is already closed. Instantiate'
                       ' a new <Parallel> object to get going again!')
            raise AssertionError(err_msg)

    @staticmethod
    def __params_type_checked(value: MockParams) -> MockParams:
        if not type(value) is MockParams:
            raise TypeError('Parameters  must be of type <MockParams>!')
        return value


