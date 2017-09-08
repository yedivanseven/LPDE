from multiprocessing import Event as Stop
from multiprocessing import Process, Value
from pandas import DataFrame
from sklearn.neighbors import KernelDensity
from ..datatypes import Event, Action, Kernel
from ..geometry import BoundingBox
from ..producers import PRODUCER_TYPES

KDE_PARAMS = {'rtol': 0.0}


class Estimator(Process):
    def __init__(self, kernel: Kernel, bounds: BoundingBox, producer) -> None:
        super().__init__()
        kernel = self.__kernel_type_checked(kernel)
        self.__bounds = self.__boundingbox_type_checked(bounds)
        self.__produce = self.__producer_type_checked(producer)
        self.__n = Value('i', 0)
        self.__stop = Stop()
        self.__data = DataFrame(columns=('x', 'y'))
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}
        self.__estimator = KernelDensity(bandwidth=kernel.bandwidth,
                                         kernel=kernel.name,
                                         **KDE_PARAMS)

    @property
    def n_points(self) -> int:
        return self.__n.value

    @property
    def stop(self):
        return self.__stop

    def run(self):
        while not self.__stop.is_set():
            try:
                event = self.__verified(next(self.__produce.data))
            except (TypeError, ValueError):
                pass
            else:
                handle = self.__handler_of[event.action]
                handle(event)
                if self.__data.size > 0:
                    self.__estimator.fit(self.__data.values)

    def __add(self, event: Event) -> bool:
        if event.id not in self.__data.index:
            self.__data.loc[event.id, :] = event.location.position
            with self.__n.get_lock():
                self.__n.value += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__data.index:
            self.__data.loc[event.id, :] = event.location.position
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__data.index:
            self.__data.drop(event.id, inplace=True)
            with self.__n.get_lock():
                self.__n.value -= 1
            return True
        return False

    def __verified(self, value: Event) -> Event:
        if type(value) is not Event:
            raise TypeError('Type of event must be <Event>!')
        if value.location and not self.__bounds.contain(value.location):
            raise ValueError('Event location is outside bounding box!')
        return value

    @staticmethod
    def __kernel_type_checked(value: Kernel) -> Kernel:
        if type(value) is not Kernel:
            raise TypeError('Kernel must be of type <Kernel>!')
        return value

    @staticmethod
    def __boundingbox_type_checked(value: BoundingBox) -> BoundingBox:
        if type(value) is not BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    @staticmethod
    def __producer_type_checked(value):
        if type(value) not in PRODUCER_TYPES:
            raise TypeError('Type of producer must be in PRODUCER_TYPES!')
        return value
