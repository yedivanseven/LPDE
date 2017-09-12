from time import sleep
from typing import Callable
from random import randint, expovariate, sample
from uuid import uuid4
from multiprocessing import Process, Queue
from queue import Full
from numpy import float64
from ..geometry import PointAt, Window, BoundingBox
from ..estimators.datatypes import Action, Event, Flags

QUEUE = type(Queue())
TIMEOUT: float = 1.0
DIST_TYPE = Callable[[BoundingBox], PointAt]


class MockParams:
    def __init__(self, rate: float, build_up: int, dist: callable) -> None:
        self.__rate = self.__float_type_and_range_checked(rate)
        self.__build_up = self.__integer_type_and_range_checked(build_up)
        self.__dist = self.__function_type_checked(dist)

    @property
    def rate(self) -> float:
        return self.__rate

    @property
    def build_up(self) -> int:
        return self.__build_up

    @property
    def dist(self) -> DIST_TYPE:
        return self.__dist

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Rate parameter must be a number!')
        if value <= 0.0:
            raise ValueError('Rate parameter must be positive!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if type(value) is not int:
            raise TypeError('Build-up and number of events must be integers!')
        if value <= 0:
            raise ValueError('Build-up and number of events must be positive!')
        return value

    @staticmethod
    def __function_type_checked(value: DIST_TYPE) -> DIST_TYPE:
        if not callable(value):
            raise TypeError('Distribution must be callable!')
        center = PointAt(0, 0)
        window = Window(3, 2)
        bounds = BoundingBox(center, window)
        try:
            return_value = value(bounds)
        except Exception:
            raise RuntimeError('Test call to distribution function failed!')
        if type(return_value) is not PointAt:
            raise TypeError('Return value of distribution must be <PointAt>!')
        if not bounds.contain(return_value):
            raise ValueError('Returned test point lies outside bounding box!')
        return value


class MockProducer(Process):
    def __init__(self, params: MockParams, bounds: BoundingBox,
                 event_queue: QUEUE) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__bounds = self.__bounds_type_checked(bounds)
        self.__event_queue = self.__queue_type_checked(event_queue)
        self.__flag = Flags()
        self.__points = {}
        self.__according_to = {1: self.__add,
                               0: self.__move,
                              -1: self.__delete}

    @property
    def flag(self) -> Flags:
        return self.__flag

    def run(self) -> None:
        n_points = 0
        while not self.__flag.stop.is_set():
            if n_points < self.__params.build_up:
                event = self.__add()
                n_points += 1
            else:
                event_type = randint(-1, 1) if self.__points else 1
                event = self.__according_to[event_type]()
            self.__push(event)
        self.__flag.done.set()

    def __add(self) -> Event:
        location = self.__new_location()
        uuid = uuid4()
        self.__points[uuid] = location
        return Event(uuid, Action.ADD, location)

    def __move(self) -> Event:
        location = self.__new_location()
        uuid = sample(self.__points.keys(), 1)[0]
        self.__points[uuid] = location
        return Event(uuid, Action.MOVE, location)

    def __delete(self) -> Event:
        uuid = sample(self.__points.keys(), 1)[0]
        _ = self.__points.pop(uuid)
        return Event(uuid, Action.DELETE)

    def __push(self, event: Event) -> None:
        sleep(expovariate(self.__params.rate))
        try:
            self.__event_queue.put(event, timeout=TIMEOUT)
        except AssertionError:
            err_msg = ('Event queue is already closed. Instantiate'
                       ' a new <Parallel> object to get going again!')
            raise AssertionError(err_msg)
        except Full:
            raise Full('Event queue is full!')

    def __new_location(self) -> PointAt:
        location: PointAt = self.__params.dist(self.__bounds)
        if not self.__bounds.contain(location):
            raise ValueError('Distribution returned point out of bounds!')
        return location

    @staticmethod
    def __params_type_checked(value: MockParams) -> MockParams:
        if type(value) is not MockParams:
            raise TypeError('Parameters must be of type <MockParams>!')
        return value

    @staticmethod
    def __bounds_type_checked(value: BoundingBox) -> BoundingBox:
        if type(value) is not BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if type(value) is not QUEUE:
            raise TypeError('Event queue must be a multiprocessing Queue!')
        if value._closed:
            raise OSError('Event queue must be open on instantiation!')
        return value
