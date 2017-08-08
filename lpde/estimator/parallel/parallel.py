from multiprocessing import Array, Queue
from numpy import square, ndarray, float64, frombuffer
from numpy.polynomial.legendre import legvander2d, legval2d
from pandas import DataFrame
from .smoother import Smoother
from .minimizer import Minimizer
from ...geometry import Mapper, PointAt
from ..datatypes import Coefficients, Scalings, Event, Degree, Action, Signal
from ..datatypes import SmootherParams, MinimizerParams

GRADIENT_TOLERANCE = 0.1
MAXIMUM_ITERATIONS = 10000


class ParallelEstimate:
    def __init__(self, degree: Degree, mapper: Mapper) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__map = self.__mapper_type_checked(mapper)
        self.__c = Coefficients(self.__degree)
        self.__scale = Scalings(self.__degree)
        self.__phi_ijn = DataFrame(index=range(self.__c.mat.size))
        self.__handler_of = {Action.ADD: self.__add,
                             Action.MOVE: self.__move,
                             Action.DELETE: self.__delete}
        self.__N = 0
        self.__control = Queue()
        self.__phi_queue = Queue()
        self.__coeff_queue = Queue()
        self.__smoothed = Array('d', self.__c.vec)
        self.__c.vec = frombuffer(self.__smoothed.get_obj())

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

    def at(self, point: PointAt) -> float64:
        point = self.__point_type_checked(point)
        mapped_point = self.__map.in_from(point)
        p = square(legval2d(*mapped_point, self.__c.mat/self.__scale.mat))
        return self.__map.out(p)

    def update_with(self, event: Event) -> None:
        event = self.__event_type_checked(event)
        data_changed_due_to = self.__handler_of[event.action]
        if data_changed_due_to(event):
            self.__phi_queue.put(self.__phi_ijn.values)

    def __add(self, event: Event) -> bool:
        if event.id not in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            self.__N += 1
            return True
        return False

    def __move(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            location = self.__map.in_from(event.location)
            phi_ijn = legvander2d(*location, self.__degree)[0]/self.__scale.vec
            self.__phi_ijn.loc[:, event.id] = phi_ijn
            return True
        return False

    def __delete(self, event: Event) -> bool:
        if event.id in self.__phi_ijn.columns:
            self.__phi_ijn.drop(event.id, axis=1, inplace=True)
            self.__N -= 1
            return True
        return False

    def _on(self, x_grid: ndarray, y_grid: ndarray) -> ndarray:
        return square(legval2d(x_grid, y_grid, self.__c.mat/self.__scale.mat))

    @property
    def _phi_queue_empty(self) -> bool:
        return self.__phi_queue.empty()

    @property
    def _c(self) -> ndarray:
        return self.__c.vec

    @property
    def _phi(self) -> DataFrame:
        return self.__phi_ijn

    @property
    def _N(self) -> int:
        return self.__N

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
    def __point_type_checked(value: PointAt) -> PointAt:
        if not type(value) is PointAt:
            raise TypeError('Point must be of type <PointAt>!')
        return value

    @staticmethod
    def __event_type_checked(value: Event) -> Event:
        if not type(value) is Event:
            raise TypeError('Event must be of type <Event>!')
        return value

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Number of processes must be an integer!')
        if value < 1:
            raise ValueError('Number of processes must be at least 1!')
        return value
