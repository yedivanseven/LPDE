from multiprocessing import Process
from queue import Empty
from numpy import frombuffer, exp
from time import perf_counter
from ..datatypes import SmootherParams

STOP = 'stop'
CONTINUE = 'continue'


class Smoother(Process):
    def __init__(self, params: SmootherParams) -> None:
        super().__init__()
        self.__params = self.__type_checked(params)
        self.__control = CONTINUE
        self.__initial = frombuffer(self.__params.smoothed.get_obj()).copy()

    def run(self):
        raw = smoothed = self.__initial.copy()
        while self.__control != STOP:
            try:
                start = perf_counter()
                raw = self.__params.coefficients.get_nowait()
            except Empty:
                pass
            delta = perf_counter() - start
            damping = 1.0 - exp(-delta / self.__params.decay)
            smoothed = damping * raw + (1.0 - damping) * smoothed
            self.__params.smoothed.get_obj()[:] = smoothed
            try:
                self.__control = self.__params.control.get_nowait()
            except Empty:
                self.__control = CONTINUE

    @staticmethod
    def __type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value
