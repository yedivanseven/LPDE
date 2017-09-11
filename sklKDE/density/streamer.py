from multiprocessing import Event as Stop
from multiprocessing import Process
from .parameters import StreamerParams
from ..datatypes import Event, Action


class Streamer(Process):
    def __init__(self, params: StreamerParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__stop = Stop()
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}

    @property
    def stop(self):
        return self.__stop

    def run(self) -> None:
        while not self.__stop.is_set():
            try:
                event = self.__verified(next(self.__params.producer.data))
            except (TypeError, ValueError):
                raise
            except StopIteration:
                raise StopIteration('Producer does not yield any more points!')
            else:
                handle = self.__handler_of[event.action]
                handle(event)

    def __add(self, event: Event):
        if event.id not in self.__params.data.keys():
            self.__params.data[event.id] = event.location.position

    def __move(self, event: Event):
        if event.id in self.__params.data.keys():
            self.__params.data[event.id] = event.location.position

    def __delete(self, event: Event):
        if event.id in self.__params.data.keys():
            _ = self.__params.data.pop(event.id)

    def __verified(self, value: Event) -> Event:
        if type(value) is not Event:
            raise TypeError('Type of event must be <Event>!')
        if value.location and not self.__params.bounds.contain(value.location):
            raise ValueError('Event location is outside bounding box!')
        return value

    @staticmethod
    def __params_type_checked(value: StreamerParams) -> StreamerParams:
        if type(value) is not StreamerParams:
            raise TypeError('Parameters must be of type <StreamerParams>!')
        return value
