from multiprocessing import Process
from queue import Empty
from numpy import frombuffer, exp, ndarray
from time import perf_counter
from ..datatypes import SmootherParams, Control


class Smoother(Process):
    def __init__(self, params: SmootherParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__control = Control.CONTINUE
        self.__initial = frombuffer(self.__params.smoothed.get_obj()).copy()

    def run(self):
        raw = smoothed = self.__initial.copy()
        while self.__control != Control.STOP:
            try:
                start_time = perf_counter()
                from_queue = self.__params.coefficients.get_nowait()
                raw = self.__array_type_checked(from_queue)
            except Empty:
                pass
            time_difference = perf_counter() - start_time
            damping = 1.0 - exp(-time_difference / self.__params.decay)
            smoothed = damping * raw + (1.0 - damping) * smoothed
            self.__params.smoothed.get_obj()[:] = smoothed
            try:
                self.__control = self.__params.control.get_nowait()
            except Empty:
                self.__control = Control.CONTINUE

    @staticmethod
    def __params_type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value

    @staticmethod
    def __array_type_checked(value: ndarray) -> ndarray:
        if not type(value) is ndarray:
            raise TypeError('Coefficients must be numpy array!')
        return value
