from multiprocessing import Process, Queue, Array
from numpy import float64
from .transformer import TransformerParams, Transformer
from .minimizer import MinimizerParams, Minimizer
from .smoother import SmootherParams, Smoother
from ..datatypes import Degree, Coefficients
from ...geometry import Mapper
from ...producers import MockProducer, PRODUCER_TYPES

QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class Controller:
    def __init__(self, degree: Degree, mapper: Mapper, produce_params) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__mapper = self.__mapper_type_checked(mapper)
        self.__produce_params = self.__params_type_checked(produce_params)
        self.__event_queue = Queue()
        self.__phi_queue = Queue()
        self.__coeff_queue = Queue()
        self.__queues = (self.__event_queue,
                         self.__phi_queue,
                         self.__coeff_queue)
        self.__smooth_coeffs = Array('d', Coefficients(self.__degree).vec)
        self.__transformer_params = TransformerParams(self.__degree,
                                                      self.__mapper,
                                                      self.__event_queue,
                                                      self.__phi_queue)
        self.__minimizer_params = MinimizerParams(self.__degree,
                                                  self.__phi_queue,
                                                  self.__coeff_queue)
        self.__smoother_params = SmootherParams(self.__coeff_queue,
                                                self.__smooth_coeffs)
        self.__minimizers = []
        self.__class_prefix = '_' + self.__class__.__name__ + '__'

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
    def producer(self) -> Process:
        if self.__has('producer'):
            return self.__producer
        raise AttributeError('Producer process not started yet!')

    @property
    def transformer(self) -> Process:
        if self.__has('transformer'):
            return self.__transformer
        raise AttributeError('Transformer process not started yet!')

    @property
    def minimizers(self) -> list:
        if self.__minimizers:
            return self.__minimizers
        raise AttributeError('Minimizer process(es) not started yet!')

    @property
    def smoother(self) -> Process:
        if self.__has('smoother'):
            return self.__smoother
        raise AttributeError('Smoother process not started yet!')

    @property
    def alive(self) -> dict:
        living = {'producer': False, 'transformer': False, 'smoother': False}
        if self.__has('producer') and self.__producer.is_alive():
            living['producer'] = True
        if self.__has('transformer') and self.__transformer.is_alive():
            living['transformer'] = True
        if self.__has('smoother') and self.__smoother.is_alive():
            living['smoother'] = True
        living['minimizers'] = tuple(m.is_alive() for m in self.__minimizers)
        return living

    @property
    def open(self) -> dict:
        not_closed = {'events': False, 'phi': False, 'coefficients': False}
        if not self.__event_queue._closed:
            not_closed['events'] = True
        if not self.__phi_queue._closed:
            not_closed['phi'] = True
        if not self.__coeff_queue._closed:
            not_closed['coefficients'] = True
        return not_closed

    @property
    def qsize(self) -> dict:
        qsizes = {'events': None, 'phi': None, 'coefficients': None}
        if not self.__event_queue._closed:
            qsizes['events'] = self.__event_queue.qsize()
        if not self.__phi_queue._closed:
            qsizes['phi'] = self.__phi_queue.qsize()
        if not self.__coeff_queue._closed:
            qsizes['coefficients'] = self.__coeff_queue.qsize()
        return qsizes

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
        self.__start_smoother(decay)
        self.__start_minimizers(n_jobs)
        self.__start_transformer()
        self.__start_producer()

    def __start_producer(self) -> None:
        if not self.__has('producer'):
            self.__producer = MockProducer(self.__produce_params,
                                           self.__mapper.bounds,
                                           self.__event_queue)
            self.__producer.start()

    def __start_transformer(self) -> None:
        if not self.__has('transformer'):
            self.__transformer = Transformer(self.__transformer_params)
            self.__transformer.start()

    def __start_minimizers(self, n_jobs: int =1) -> None:
        n_jobs = self.__integer_type_and_range_checked(n_jobs)
        for n in range(n_jobs):
            minimizer = Minimizer(self.__minimizer_params)
            self.__minimizers.append(minimizer)
            minimizer.start()

    def __start_smoother(self, decay: float =1.0) -> None:
        decay = self.__float_type_and_range_checked(decay)
        if not self.__has('smoother'):
            self.__smoother = Smoother(self.__smoother_params, decay)
            self.__smoother.start()

    def stop(self) -> None:
        self.__stop_processes()
        self.__join_processes()
        self.__close_queues()

    def __stop_processes(self) -> None:
        if self.__has('producer'):
            self.__producer.flag.stop.set()
            self.__producer.flag.done.wait()
        if self.__has('transformer'):
            self.__transformer.flag.stop.set()
            self.__transformer.flag.done.wait()
        for minimizer in self.__minimizers:
            minimizer.flag.stop.set()
            minimizer.flag.done.wait()
        if self.__has('smoother'):
            self.__smoother.flag.stop.set()
            self.__smoother.flag.done.wait()

    def __join_processes(self) -> None:
        if self.__has('producer'):
            self.__producer.join()
        if self.__has('transformer'):
            self.__transformer.join()
        for minimizer in self.__minimizers:
            minimizer.join()
        if self.__has('smoother'):
            self.__smoother.join()

    def __close_queues(self) -> None:
        for queue in self.__queues:
            queue.close()
            queue.join_thread()

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
    def __params_type_checked(value):
        if type(value) not in PRODUCER_TYPES:
            err_msg = 'Type of producer parameters must be in PRODUCER_TYPES!'
            raise TypeError(err_msg)
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if type(value) is not int:
            raise TypeError('Number of worker processes must be an integer!')
        if value < 1:
            raise ValueError('Number of worker processes must be at least 1!')
        return value

    @staticmethod
    def __float_type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Decay constant must be a number!')
        if value <= 0:
            raise ValueError('Decay constant must be positive > 0!')
        return value

    def __has(self, attribute):
        return hasattr(self, self.__class_prefix + attribute)
