from multiprocessing import Queue, Array
from ..datatypes import Degree, Coefficients, Signal
from ..datatypes import SmootherParams, MinimizerParams
from .smoother import Smoother
from .minimizer import Minimizer


class Estimator:
    def __init__(self, degree: Degree):
        self.__degree = self.__degree_type_checked(degree)
        self.__c = Coefficients(self.__degree)
        self.__control = Queue()
        self.__phi_queue = Queue()
        self.__coeff_queue = Queue()
        self.__smoothed = Array('d', self.__c.vec)

    @property
    def phi_queue(self):
        return self.__phi_queue

    @property
    def smoothed(self):
        return self.__smoothed

    def start(self, decay: float =1.0, n_jobs: int = 1) -> None:
        self.__start_smoother(decay)
        self.__start_minimizers(n_jobs)

    def __start_minimizers(self, n_jobs: int =1) -> None:
        n_jobs = self.__integer_type_and_range_checked(n_jobs)
        minimize_params = MinimizerParams(self.__degree, self.__control,
                                          self.__phi_queue, self.__coeff_queue)
        self.__minimizers = [Minimizer(minimize_params) for _ in range(n_jobs)]
        for n in range(n_jobs):
            self.__minimizers[n].start()

    def __start_smoother(self, decay: float =1.0) -> None:
        smoother_params = SmootherParams(self.__control, self.__coeff_queue,
                                         self.__smoothed, decay)
        self.__smoother = Smoother(smoother_params)
        self.__smoother.start()

    def stop(self) -> None:
        self.__stop_processes()
        self.__close_queues()

    def __stop_processes(self) -> None:
        for _ in self.__minimizers:
            self.__control.put(Signal.STOP)
        self.__control.put(Signal.STOP)
        for minimizer in self.__minimizers:
            if minimizer.is_alive():
                minimizer.join()
        if self.__smoother.is_alive():
            self.__smoother.join()

    def __close_queues(self) -> None:
        queues = (self.__phi_queue, self.__coeff_queue, self.__control)
        for queue in queues:
            if not queue._closed:
                queue.close()
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

