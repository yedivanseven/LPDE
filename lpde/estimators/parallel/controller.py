from multiprocessing import Process, Queue, Array
from time import sleep
from numpy import float64
from ..datatypes import Degree, Coefficients, Signal
from ...geometry import Mapper
from .smootherparams import SmootherParams
from .smoother import Smoother
from .minimizerparams import MinimizerParams
from .minimizer import Minimizer
from .transformerparams import TransformerParams
from .transformer import Transformer

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))
QUEUE_CLOSE_TIMEOUT = 1e-6


class Controller:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__mapper = self.__mapper_type_checked(mapper)
        self.__control_queue = Queue()
        self.__event_queue = Queue()
        self.__phi_queue = Queue()
        self.__coeff_queue = Queue()
        self.__queues = (self.__control_queue,
                         self.__event_queue,
                         self.__phi_queue,
                         self.__coeff_queue)
        self.__smooth_coeffs = Array('d', Coefficients(self.__degree).vec)
        self.__transformer_params = TransformerParams(self.__degree,
                                                      self.__mapper,
                                                      self.__control_queue,
                                                      self.__event_queue,
                                                      self.__phi_queue)
        self.__minimizer_params = MinimizerParams(self.__degree,
                                                  self.__control_queue,
                                                  self.__phi_queue,
                                                  self.__coeff_queue)
        self.__minimizers = []
        self.__class_prefix = '_' + self.__class__.__name__ + '__'

    @property
    def control_queue(self) -> QUEUE:
        return self.__control_queue

    @property
    def event_queue(self) -> QUEUE:
        return self.__event_queue

    @property
    def phi_queue(self) -> QUEUE:
        return self.__phi_queue

    @property
    def coeff_queue(self) -> QUEUE:
        return self.__coeff_queue

    @property
    def transformer(self) -> Process:
        if self.__has('transformer'):
            return self.__transformer
        raise AttributeError('Transformer process not started yet!')

    @property
    def minimizers(self) -> list:
        if self.__minimizers:
            return self.__minimizers
        raise AttributeError('Minimizer processe(s) not started yet!')

    @property
    def smoother(self) -> Process:
        if self.__has('smoother'):
            return self.__smoother
        raise AttributeError('Smoother process not started yet!')

    @property
    def all_alive(self) -> bool:
        alive = False
        if self.__has('transformer'):
            alive = alive or self.__transformer.is_alive()
        for minimizer in self.__minimizers:
            alive= alive and minimizer.is_alive()
        if self.__has('smoother'):
            alive = alive and self.__smoother.is_alive()
        return alive

    @property
    def n_jobs(self) -> int:
        return len(self.__minimizers)

    @property
    def N(self) -> int:
        return self.__transformer.N if self.__has('transformer') else 0

    @property
    def smooth_coeffs(self) -> ARRAY:
        return self.__smooth_coeffs

    def start(self, n_jobs: int =1, decay: float =1.0) -> None:
        if any(queue._closed for queue in self.__queues):
            raise OSError('Some queues have been closed. Instantiate a'
                          ' new <Parallel> object to get going again!')
        self.__start_transformer()
        self.__start_minimizers(n_jobs)
        self.__start_smoother(decay)

    def __start_transformer(self) -> None:
        if not self.__has('transformer'):
            self.__transformer = Transformer(self.__transformer_params)
            self.__transformer.start()

    def __start_minimizers(self, n_jobs: int =1) -> None:
        n_jobs = self.__integer_type_and_range_checked(n_jobs)
        for n in range(n_jobs):
            minimizer = Minimizer(self.__minimizer_params)
            minimizer.start()
            self.__minimizers.append(minimizer)

    def __start_smoother(self, decay: float =1.0) -> None:
        decay = self.__float_type_and_range_checked(decay)
        if not self.__has('smoother'):
            params = SmootherParams(self.__control_queue, self.__coeff_queue,
                                    self.__smooth_coeffs, decay)
            self.__smoother = Smoother(params)
            self.__smoother.start()

    def stop(self) -> None:
        self.__stop_processes()
        self.__close_queues()

    def __stop_processes(self) -> None:
        try:
            for _ in self.__minimizers:
                self.__control_queue.put(Signal.STOP)
            self.__control_queue.put(Signal.STOP)
            self.__control_queue.put(Signal.STOP)
        except AssertionError:
            pass
        if self.__has('transformer') and self.__transformer.is_alive():
            self.__transformer.join()
        for minimizer in self.__minimizers:
            if minimizer.is_alive():
                minimizer.join()
        if self.__has('smoother') and self.__smoother.is_alive():
            self.__smoother.join()

    def __close_queues(self) -> None:
        for queue in self.__queues:
            queue.close()
            sleep(QUEUE_CLOSE_TIMEOUT)
            queue.join_thread()

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if not type(value) is Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __mapper_type_checked(value: Mapper) -> Mapper:
        if not type(value) is Mapper:
            raise TypeError('Type of mapper must be <Mapper>!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Number of processes must be an integer!')
        if value < 1:
            raise ValueError('Number of processes must be at least 1!')
        return value

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if not type(value) in (int, float, float64):
            raise TypeError('Decay constant must be a number!')
        if value <= 0:
            raise ValueError('Decay constant must be positive !')
        return value

    def __has(self, attribute):
        return hasattr(self, self.__class_prefix + attribute)
