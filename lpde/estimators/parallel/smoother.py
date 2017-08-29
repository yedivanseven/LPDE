from multiprocessing import Process, Queue, Array
from queue import Empty
from numpy import frombuffer, exp, ndarray, float64
from time import perf_counter
from ..datatypes import Flags

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))
STOP = 1  # Queue-get timeout in seconds for process termination.


class SmootherParams():
    def __init__(self, coeff_queue: QUEUE, smooth_coeffs: ARRAY) -> None:
        self.__coeff_queue = self.__queue_type_checked(coeff_queue)
        self.__smooth_coeffs = self.__array_type_checked(smooth_coeffs)

    @property
    def coeff_queue(self) -> QUEUE:
        return self.__coeff_queue

    @property
    def smooth_coeffs(self) -> ARRAY:
        return self.__smooth_coeffs

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if type(value) is not QUEUE:
            raise TypeError('Coeff. queue must be a multiprocessing Queue!')
        if value._closed:
            raise OSError('Coefficient queue mut be open on instantiation!')
        return value

    @staticmethod
    def __array_type_checked(value: ARRAY) -> ARRAY:
        if type(value) is not ARRAY:
            raise TypeError('Smooth coefficients must be a shared Array!')
        return value


class Smoother(Process):
    def __init__(self, params: SmootherParams, decay: float) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__decay = self.__float_type_and_range_checked(decay)
        self.__flag = Flags()
        self.__init = frombuffer(self.__params.smooth_coeffs.get_obj()).copy()
        self.__shape = self.__init.shape

    @property
    def flag(self) -> Flags:
        return self.__flag

    def run(self) -> None:
        raw_coeffs = self.__init.copy()
        smooth_coeffs = self.__init.copy()
        while True:
            block = self.__flag.stop.is_set()
            start_time = perf_counter()
            try:
                item = self.__params.coeff_queue.get(block=block, timeout=STOP)
                raw_coeffs = self.__type_and_shape_checked(item)
            except OSError:
                raise OSError('Coefficient queue has been closed. Instantiate'
                              ' a new <Parallel> object to get going again!')
            except Empty:
                if self.__flag.stop.is_set():
                    break
            time_difference = perf_counter() - start_time
            damping = 1.0 - exp(-time_difference / self.__decay)
            smooth_coeffs = damping*raw_coeffs + (1.0-damping)*smooth_coeffs
            with self.__params.smooth_coeffs.get_lock():
                self.__params.smooth_coeffs.get_obj()[:] = smooth_coeffs
        self.__flag.done.set()

    @staticmethod
    def __params_type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Decay constant must be a number!')
        if value <= 0:
            raise ValueError('Decay constant must be positive !')
        return value

    def __type_and_shape_checked(self, value: ndarray) -> ndarray:
        if type(value) is not ndarray:
            raise TypeError('Coefficients must be numpy array!')
        if value.shape != self.__shape:
            raise ValueError('Read coefficient array with wrong shape! Should'
                             f' be {self.__shape}, but is now {value.shape}.')
        return value
