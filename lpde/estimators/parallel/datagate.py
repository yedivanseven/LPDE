from multiprocessing import Process, Queue, Value
from multiprocessing.connection import Connection
from queue import Full
from numpy import ndarray
from pandas import DataFrame
from ..datatypes import Scalings, Action, Event, Degree, Flags
from ...geometry import Mapper

QUEUE = type(Queue())
TIMEOUT: float = 1.0


class DataGateParams:
    def __init__(self, degree: Degree, mapper: Mapper, event_pipe: Connection,
                 point_queue: QUEUE) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__event_pipe = self.__connection_type_checked(event_pipe)
        self.__point_queue = self.__queue_type_checked(point_queue)

    @property
    def degree(self) -> Degree:
        return self.__degree

    @property
    def map(self) -> Mapper:
        return self.__map

    @property
    def event_pipe(self) -> Connection:
        return self.__event_pipe

    @property
    def point_queue(self) -> QUEUE:
        return self.__point_queue

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if type(value) is not Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __mapper_type_checked(value: Mapper) -> Mapper:
        if type(value) is not Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return value

    @staticmethod
    def __connection_type_checked(value: Connection) -> Connection:
        if type(value) is not Connection:
            raise TypeError('Event pipe must be a multiprocessing Connection!')
        if value.closed:
            raise ValueError('Event pipe must not be closed on instantiation!')
        if value.writable or not value.readable:
            raise ValueError('Event pipe should be read-only!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if type(value) is not QUEUE:
            raise TypeError('Event and point must be multiprocessing Queues!')
        if value._closed:
            raise OSError('Event- and point-queues must initially be open!')
        return value


class DataGate(Process):
    def __init__(self, params: DataGateParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__flag = Flags()
        self.__degree = self.__params.degree
        self.__scale = Scalings(self.__degree)
        self.__points = DataFrame(index=('x', 'y'))
        self.__N = Value('i', 0)
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}

    @property
    def flag(self) -> Flags:
        return self.__flag

    @property
    def N(self) -> int:
        return self.__N.value

    def run(self) -> None:
        while True:
            if self.__params.event_pipe.poll(timeout=TIMEOUT):
                try:
                    item_from_pipe = self.__params.event_pipe.recv()
                    event = self.__event_type_checked(item_from_pipe)
                except EOFError:
                    raise EOFError('Nothing more to read from event pipe!')
                except OSError:
                    raise OSError('Event pipe appears to be closed!')
                else:
                    data_changed_due_to = self.__handler_of[event.action]
                    if data_changed_due_to(event):
                        self.__push(self.__points.values)
            elif self.__flag.stop.is_set():
                break
        self.__params.event_pipe.close()
        self.__flag.done.set()

    def __add(self, event: Event) -> bool:
        if event.id not in self.__points.columns:
            try:
                location = self.__params.map.in_from(event.location)
            except ValueError:
                return False
            else:
                self.__points.loc[:, event.id] = location
            with self.__N.get_lock():
                self.__N.value += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__points.columns:
            try:
                location = self.__params.map.in_from(event.location)
            except ValueError:
                return False
            else:
                self.__points.loc[:, event.id] = location
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__points.columns:
            self.__points.drop(event.id, axis=1, inplace=True)
            with self.__N.get_lock():
                self.__N.value -= 1
            return True
        return False

    def __push(self, array: ndarray) -> None:
        try:
            self.__params.point_queue.put(array, timeout=TIMEOUT)
        except AssertionError:
            err_msg = ('Point queue is already closed. Instantiate a'
                       ' new <Parallel> object to start all over!')
            raise AssertionError(err_msg)
        except Full:
            raise Full('Point queue is full!')

    @staticmethod
    def __params_type_checked(value: DataGateParams) -> DataGateParams:
        if type(value) is not DataGateParams:
            raise TypeError('Parameters must be of type <TransformerParams>!')
        return value

    @staticmethod
    def __event_type_checked(value: Event) -> Event:
        if type(value) is not Event:
            raise TypeError('Event must be of type <Event>!')
        return value
