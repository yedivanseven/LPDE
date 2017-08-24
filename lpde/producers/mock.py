from time import sleep
from random import randint, expovariate, sample
from uuid import uuid4
from multiprocessing import Process, Queue
from multiprocessing import Event as StopFlag
from numpy import float64
from ..geometry import PointAt, Window, BoundingBox
from ..estimators.datatypes import Action, Event

QUEUE = type(Queue())
STOP_FLAG = type(StopFlag())


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
    def dist(self) -> callable:
        return self.__dist

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Rate parameter must be a number!')
        if value <= 0.0:
            raise ValueError('Rate parameter must be positive!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value) -> int:
        if type(value) is not int:
            raise TypeError('Build-up and number of events must be integers!')
        if value <= 0:
            raise ValueError('Build-up and number of events must be positive!')
        return value

    @staticmethod
    def __function_type_checked(value: callable) -> callable:
        if not callable(value):
            raise TypeError('Distribution must be callable!')
        center = PointAt(0, 0)
        window = Window(3, 2)
        bounds = BoundingBox(center, window)
        try:
            return_value = value(bounds)
        except:
            raise RuntimeError('Call to distribution function failed!')
        if type(return_value) is not PointAt:
            raise TypeError('Return value of distribution must be <PointAt>!')
        if not bounds.contain(return_value):
            raise ValueError('Returned point lies outside bounding box!')
        return value


class MockProducer(Process):
    def __init__(self, params: MockParams, bounds: BoundingBox,
                 event_queue: QUEUE, stop_flag: STOP_FLAG) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__bounds = self.__bounds_type_checked(bounds)
        self.__stop_flag = self.__stop_type_checked(stop_flag)
        self.__event_queue = self.__queue_type_checked(event_queue)
        self.__points = {}
        self.__according_to = {1: self.__add,
                               0: self.__move,
                              -1: self.__delete}

    def run(self) -> None:
        n_points = 0
        while not self.__stop_flag.is_set():
            if n_points < self.__params.build_up:
                event = self.__add()
                self.__push(event)
                n_points += 1
            else:
                event_type = randint(-1, 1) if self.__points else 1
                event = self.__according_to[event_type]()
                self.__push(event)

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
            self.__event_queue.put(event)
        except AssertionError:
            err_msg = ('Event queue is already closed. Instantiate'
                       ' a new <Parallel> object to get going again!')
            raise AssertionError(err_msg)

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

    @staticmethod
    def __stop_type_checked(value: STOP_FLAG) -> STOP_FLAG:
        if type(value) is not STOP_FLAG:
            raise TypeError('The stop flag must be a multiprocessing Event!')
        if value.is_set():
            raise ValueError('Stop flag must not be set on instantiation!')
        return value
