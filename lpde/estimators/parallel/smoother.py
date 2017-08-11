from multiprocessing import Process
from queue import Empty
from numpy import frombuffer, exp, ndarray
from time import perf_counter
from ..datatypes import Signal
from .smootherparams import SmootherParams


class Smoother(Process):
    def __init__(self, params: SmootherParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__control = Signal.CONTINUE
        self.__init = frombuffer(self.__params.smooth_coeffs.get_obj()).copy()
        self.__shape = self.__init.shape

    def run(self):
        raw_coeffs = self.__init.copy()
        smooth_coeffs = self.__init.copy()
        while self.__control != Signal.STOP:
            start_time = perf_counter()
            try:
                item_from_queue = self.__params.coeff_queue.get_nowait()
                raw_coeffs = self.__type_and_shape_checked(item_from_queue)
            except Empty:
                pass
            except OSError:
                raise OSError('Coefficient queue has been closed. Instantiate'
                              ' a new <Parallel> object to get going again!')
            time_difference = perf_counter() - start_time
            damping = 1.0 - exp(-time_difference / self.__params.decay)
            smooth_coeffs = damping*raw_coeffs + (1.0-damping)*smooth_coeffs
            with self.__params.smooth_coeffs.get_lock():
                self.__params.smooth_coeffs.get_obj()[:] = smooth_coeffs
            try:
                self.__control = self.__params.control.get_nowait()
            except Empty:
                self.__control = Signal.CONTINUE
            except OSError:
                raise OSError('Control queue is already closed. Instantiate'
                              ' a new <Parallel> object to get going again!')

    @staticmethod
    def __params_type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value

    def __type_and_shape_checked(self, value: ndarray) -> ndarray:
        if not type(value) is ndarray:
            raise TypeError('Coefficients must be numpy array!')
        if value.shape != self.__shape:
            raise ValueError('Read-in coefficient array has wrong shape!')
        return value
