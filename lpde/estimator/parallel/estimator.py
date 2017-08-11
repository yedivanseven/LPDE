from multiprocessing import Queue, Array
from time import sleep
from ..datatypes import Degree, Coefficients, Signal
from .smootherparams import SmootherParams
from .smoother import Smoother
from .minimizerparams import MinimizerParams
from .minimizer import Minimizer

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))
QUEUE_CLOSE_TIMEOUT = 1e-6


class Estimator:
    def __init__(self, degree: Degree) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__c = Coefficients(self.__degree)
        self.__control = Queue()
        self.__phi_queue = Queue()
        self.__coeff_queue = Queue()
        self.__smoothed = Array('d', self.__c.vec)
        self.__minimizers = []
        self.__class_prefix = '_' + self.__class__.__name__ + '__'

    @property
    def phi_queue(self) -> QUEUE:
        return self.__phi_queue

    @property
    def smoothed(self) -> ARRAY:
        return self.__smoothed

    def start(self, decay: float =1.0, n_jobs: int =1) -> None:
        self.__start_smoother(decay)
        self.__start_minimizers(n_jobs)

    def __start_minimizers(self, n_jobs: int =1) -> None:
        n_jobs = self.__integer_type_and_range_checked(n_jobs)
        params = MinimizerParams(self.__degree, self.__control,
                                 self.__phi_queue, self.__coeff_queue)
        for n in range(n_jobs):
            minimizer = Minimizer(params)
            minimizer.start()
            self.__minimizers.append(minimizer)

    def __start_smoother(self, decay: float =1.0) -> None:
        smoother_params = SmootherParams(self.__control, self.__coeff_queue,
                                         self.__smoothed, decay)
        if not self.__has('smoother'):
            self.__smoother = Smoother(smoother_params)
            self.__smoother.start()

    def stop(self) -> None:
        self.__stop_processes()
        self.__close_queues()

    def __stop_processes(self) -> None:
        try:
            for _ in self.__minimizers:
                self.__control.put(Signal.STOP)
            self.__control.put(Signal.STOP)
        except AssertionError:
            pass
        for minimizer in self.__minimizers:
            if minimizer.is_alive():
                minimizer.join()
        if self.__has('smoother') and self.__smoother.is_alive():
            self.__smoother.join()

    def __close_queues(self) -> None:
        queues = (self.__phi_queue, self.__coeff_queue, self.__control)
        for queue in queues:
            queue.close()
            sleep(QUEUE_CLOSE_TIMEOUT)
            queue.join_thread()

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Number of processes must be an integer!')
        if value < 1:
            raise ValueError('Number of processes must be at least 1!')
        return value

    def __has(self, attribute):
        return hasattr(self, self.__class_prefix + attribute)

