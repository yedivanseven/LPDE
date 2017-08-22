from multiprocessing import Process, Value
from queue import Empty
from numpy import ndarray
from numpy.polynomial.legendre import legvander2d
from pandas import DataFrame
from .transformerparams import TransformerParams
from ..datatypes import Scalings, Signal, Action, Event


class Transformer(Process):
    def __init__(self, params: TransformerParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__degree = self.__params.degree
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__scale.vec.size))
        self.__N = Value('i', 0)
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}

    def run(self) -> None:
        signal = Signal.CONTINUE
        while signal != Signal.STOP:
            try:
                item_from_queue = self.__params.event_queue.get_nowait()
                event = self.__event_type_checked(item_from_queue)
            except Empty:
                pass
            except OSError:
                raise OSError('Event queue is already closed. Instantiate a'
                              ' new <Parallel> object to get going again!')
            else:
                data_changed_due_to = self.__handler_of[event.action]
                if data_changed_due_to(event):
                    self.__push(self.__phi_ijn.values)
            try:
                item_from_queue = self.__params.control_queue.get_nowait()
                signal = self.__signal_type_checked(item_from_queue)
            except Empty:
                signal = Signal.CONTINUE
            except OSError:
                raise OSError('Control queue is already closed. Instantiate'
                              ' a new <Parallel> object to get going again!')

    def __add(self, event: Event) -> bool:
        if event.id not in self.__phi_ijn.columns:
            location = self.__params.map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            with self.__N.get_lock():
                self.__N.value += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            location = self.__params.map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            self.__phi_ijn.drop(event.id, axis=1, inplace=True)
            with self.__N.get_lock():
                self.__N.value -= 1
            return True
        return False

    def __push(self, array: ndarray) -> None:
        try:
            self.__params.phi_queue.put(array)
        except AssertionError:
            err_msg = ('Phi queue is already closed. Instantiate a'
                       ' new <Parallel> object to start all over!')
            raise AssertionError(err_msg)

    @property
    def N(self) -> int:
        return self.__N.value

    @staticmethod
    def __params_type_checked(value: TransformerParams) -> TransformerParams:
        if not type(value) is TransformerParams:
            raise TypeError('Parameters must be of type <TransformerParams>!')
        return value

    @staticmethod
    def __event_type_checked(value: Event) -> Event:
        if not type(value) is Event:
            raise TypeError('Event must be of type <Event>!')
        return value

    @staticmethod
    def __signal_type_checked(value: Signal) -> Signal:
        if not type(value) is Signal:
            raise TypeError('Signal must be of type <Signal>!')
        return value
