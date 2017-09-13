from time import perf_counter
from typing import Callable, Generator
from random import randint, sample
from uuid import uuid4
from ..geometry import PointAt, Window, BoundingBox
from ..estimators.datatypes import Action, Event

DIST_TYPE = Callable[[BoundingBox], PointAt]


class MockParams:
    def __init__(self, build_up: int, dist: callable) -> None:
        self.__build_up = self.__integer_type_and_range_checked(build_up)
        self.__dist = self.__function_type_checked(dist)

    @property
    def build_up(self) -> int:
        return self.__build_up

    @property
    def dist(self) -> DIST_TYPE:
        return self.__dist

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if type(value) is not int:
            raise TypeError('Build-up must be an integer!')
        if not value > 0:
            raise ValueError('Build-up must be positive!')
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


class MockProducer:
    def __init__(self, params: MockParams, bounds: BoundingBox) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__bounds = self.__bounds_type_checked(bounds)
        self.__points = {}
        self.__according_to = {1: self.__add,
                               0: self.__move,
                              -1: self.__delete}
        self.__data = self.__event_generator()

    @property
    def data(self) -> Generator:
        return self.__data

    def __event_generator(self) -> Generator:
        n_events = 0
        start = perf_counter()
        while True:
            if n_events < self.__params.build_up:
                event = self.__add()
                n_events += 1
            else:
                event_type = randint(-1, 1) if self.__points else 1
                event = self.__according_to[event_type]()
                n_events += 1
            yield event
            if n_events == 10000:
                stop = perf_counter()
                print('Average time (in seconds) is', (stop - start)/10000)

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
