from multiprocessing import Process, Queue, Array, Pipe
from numpy import float64
from .datagate import DataGateParams, DataGate
from .minimizer import MinimizerParams, Minimizer
from .smoother import SmootherParams, Smoother
from ..datatypes import Degree, Coefficients
from ...geometry import Mapper
from ...producers import MockProducer, PRODUCER_TYPES

MAXIMAL_QUEUE_SIZE: int = 1000
QUEUE = type(Queue())
ARRAY = type(Array('d', 10))


class Controller:
    def __init__(self, degree: Degree, mapper: Mapper, produce_params) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__mapper = self.__mapper_type_checked(mapper)
        self.__produce_params = self.__params_type_checked(produce_params)
        self.__event_pipe_out, self.__event_pipe_in = Pipe(duplex=False)
        self.__point_queue = Queue(maxsize=MAXIMAL_QUEUE_SIZE)
        self.__coeff_queue = Queue(maxsize=MAXIMAL_QUEUE_SIZE)
        self.__smooth_coeffs = Array('d', Coefficients(self.__degree).vec)
        self.__datagate_params = DataGateParams(self.__degree,
                                                self.__mapper,
                                                self.__event_pipe_out,
                                                self.__point_queue)
        self.__minimizer_params = MinimizerParams(self.__degree,
                                                  self.__point_queue,
                                                  self.__coeff_queue)
        self.__smoother_params = SmootherParams(self.__coeff_queue,
                                                self.__smooth_coeffs)
        self.__minimizers = []
        self.__class_prefix = '_' + self.__class__.__name__ + '__'

    @property
    def point_queue(self) -> QUEUE:
        return self.__point_queue

    @property
    def coeff_queue(self) -> QUEUE:
        return self.__coeff_queue

    @property
    def producer(self) -> Process:
        if self.__has('producer'):
            return self.__producer
        raise AttributeError('Producer process not started yet!')

    @property
    def datagate(self) -> Process:
        if self.__has('datagate'):
            return self.__datagate
        raise AttributeError('Datagate process not started yet!')

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
        living = {'Producer': False, 'Datagate': False, 'Smoother': False}
        if self.__has('producer') and self.__producer.is_alive():
            living['Producer'] = True
        if self.__has('datagate') and self.__datagate.is_alive():
            living['Datagate'] = True
        if self.__has('smoother') and self.__smoother.is_alive():
            living['Smoother'] = True
        living['Minimizers'] = tuple(m.is_alive() for m in self.__minimizers)
        return living

    @property
    def open(self) -> dict:
        not_closed = {'Events in': False, 'Events out': False,
                      'Points': False, 'Coefficients': False}
        if not self.__event_pipe_in.closed:
            not_closed['Events in'] = True
        if not self.__event_pipe_out.closed:
            not_closed['Events out'] = True
        if not self.__point_queue._closed:
            not_closed['Points'] = True
        if not self.__coeff_queue._closed:
            not_closed['Coefficients'] = True
        return not_closed

    @property
    def qsize(self) -> dict:
        qsizes = {'Points': None, 'Coefficients': None}
        if not self.__point_queue._closed:
            qsizes['Points'] = self.__point_queue.qsize()
        if not self.__coeff_queue._closed:
            qsizes['Coefficients'] = self.__coeff_queue.qsize()
        return qsizes

    @property
    def n_jobs(self) -> int:
        return len(self.__minimizers)

    @property
    def N(self) -> int:
        return self.__datagate.N if self.__has('datagate') else 0

    @property
    def smooth_coeffs(self) -> ARRAY:
        return self.__smooth_coeffs

    def start(self, n_jobs: int =1, decay: float =1.0) -> None:
        if self.__point_queue._closed or self.__coeff_queue._closed:
            raise OSError('Some queues have been closed. Instantiate a'
                          ' new <Parallel> object to get going again!')
        self.__start_smoother(decay)
        self.__start_minimizers(n_jobs)
        self.__start_datagate()
        self.__start_producer()

    def __start_producer(self) -> None:
        if not self.__has('producer'):
            self.__producer = MockProducer(self.__produce_params,
                                           self.__mapper.bounds,
                                           self.__event_pipe_in)
            self.__producer.start()

    def __start_datagate(self) -> None:
        if not self.__has('datagate'):
            self.__datagate = DataGate(self.__datagate_params)
            self.__datagate.start()

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
        self.__close_pipe_and_queues()

    def __stop_processes(self) -> None:
        if self.__has('producer'):
            self.__producer.flag.stop.set()
            self.__producer.flag.done.wait()
        if self.__has('datagate'):
            self.__datagate.flag.stop.set()
            self.__datagate.flag.done.wait()
        for minimizer in self.__minimizers:
            minimizer.flag.stop.set()
            minimizer.flag.done.wait()
        if self.__has('smoother'):
            self.__smoother.flag.stop.set()
            self.__smoother.flag.done.wait()

    def __join_processes(self) -> None:
        if self.__has('producer'):
            self.__producer.join()
        if self.__has('datagate'):
            self.__datagate.join()
        for minimizer in self.__minimizers:
            minimizer.join()
        if self.__has('smoother'):
            self.__smoother.join()

    def __close_pipe_and_queues(self) -> None:
        self.__event_pipe_in.close()
        self.__event_pipe_out.close()
        self.__point_queue.close()
        self.__point_queue.join_thread()
        self.__coeff_queue.close()
        self.__coeff_queue.join_thread()

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
