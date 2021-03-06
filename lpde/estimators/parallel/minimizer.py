from multiprocessing import Process, Queue
from queue import Empty, Full
from numpy import zeros, square, log, ndarray, float64, array
from numpy.polynomial.legendre import legvander2d
from scipy.optimize import fmin_l_bfgs_b, minimize
from ..datatypes import LagrangeCoefficients, Degree, Flags
from ..datatypes import Scalings

QUEUE = type(Queue())
GRADIENT_TOLERANCE: float = 0.1
MAXIMUM_ITERATIONS: int = 10000
TIMEOUT: float = 1.0


class MinimizerParams:
    def __init__(self, degree: Degree, point_queue: QUEUE,
                 coeff_queue: QUEUE) -> None:
        self.__degree = self.__degree_type_checked(degree)
        self.__point_queue = self.__queue_type_checked(point_queue)
        self.__coeff_queue = self.__queue_type_checked(coeff_queue)

    @property
    def degree(self):
        return self.__degree

    @property
    def point_queue(self):
        return self.__point_queue

    @property
    def coeff_queue(self):
        return self.__coeff_queue

    @staticmethod
    def __degree_type_checked(value: Degree) -> Degree:
        if type(value) is not Degree:
            raise TypeError('Polynomial degree must be of type <Degree>!')
        return value

    @staticmethod
    def __queue_type_checked(value: QUEUE) -> QUEUE:
        if type(value) is not QUEUE:
            raise TypeError('Point and coeff must be multiprocessing Queues!')
        if value._closed:
            raise OSError('Point- and coeff-queues must initially be open!')
        return value


class Minimizer(Process):
    def __init__(self, params: MinimizerParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__flag = Flags()
        self.__c_init = LagrangeCoefficients(self.__params.degree)
        self.__grad_c = zeros(self.__c_init.vector.size)
        self.__phi_ijn = array([])
        self.__scale = Scalings(self.__params.degree)
        self.__options = {'maxiter': MAXIMUM_ITERATIONS,
                          'disp': False}
        self.__constraint = {'type': 'eq',
                             'fun': self.__norm,
                             'jac': self.__grad_norm}

    @property
    def flag(self) -> Flags:
        return self.__flag

    def run(self) -> None:
        while True:
            try:
                queue_item = self.__params.point_queue.get(timeout=TIMEOUT)
                points = self.__type_and_shape_checked(queue_item)
            except OSError:
                raise OSError('Point queue is already closed. Instantiate a'
                              ' new <Parallel> object to get going again!')
            except Empty:
                if self.__flag.stop.is_set():
                    break
            else:
                self.__phi_ijn = legvander2d(*points, self.__params.degree).T/\
                                 self.__scale.vecT
                self.__minimize()
        self.__flag.done.set()

    def __minimize(self) -> None:
        self.__c_init.lagrange = self.__phi_ijn.shape[1]
        coefficients, _, status = fmin_l_bfgs_b(self.__lagrangian,
                                                self.__c_init.vector,
                                                self.__grad_lagrangian,
                                                **self.__options)
        converged = self.__grad_c.dot(self.__grad_c) < GRADIENT_TOLERANCE
        if (status['warnflag'] == 0) and converged:
            self.__push(coefficients[1:])
        else:
            self.__fallback()

    def __fallback(self) -> None:
        result = minimize(self.__neg_log_l, self.__c_init.coeffs,
                          method='slsqp',
                          jac=self.__grad_neg_log_l,
                          constraints=self.__constraint,
                          options=self.__options)
        if result.success:
            self.__push(result.x)

    def __push(self, coefficients: ndarray) -> None:
        try:
            self.__params.coeff_queue.put(coefficients, timeout=TIMEOUT)
        except AssertionError:
            err_msg = ('Coefficient queue is already closed. Instantiate'
                       ' a new <Parallel> object to get going again!')
            raise AssertionError(err_msg)
        except Full:
            raise Full('Coefficient queue is full!')

    def __lagrangian(self, c: ndarray) -> float64:
        return self.__neg_log_l(c[1:]) + c[0]*self.__norm(c[1:])

    def __grad_lagrangian(self, c: ndarray) -> ndarray:
        self.__grad_c[0] = self.__norm(c[1:])
        self.__grad_c[1:] = self.__grad_neg_log_l(c[1:]) + 2.0*c[0]*c[1:]
        return self.__grad_c

    def __neg_log_l(self, c: ndarray) -> float64:
        return -log(square(c.dot(self.__phi_ijn))).sum()

    def __grad_neg_log_l(self, c: ndarray) -> ndarray:
        return -2.0*(self.__phi_ijn/c.dot(self.__phi_ijn)).sum(axis=1)

    @staticmethod
    def __norm(c: ndarray) -> float64:
        return c.dot(c) - float64(1.0)

    @staticmethod
    def __grad_norm(c: ndarray) -> ndarray:
        return 2.0 * c

    @staticmethod
    def __params_type_checked(value: MinimizerParams) -> MinimizerParams:
        if type(value) is not MinimizerParams:
            raise TypeError('Parameters must be of type <MinimizerParams>!')
        return value

    def __type_and_shape_checked(self, value: ndarray) -> ndarray:
        if type(value) is not ndarray:
            raise TypeError('Matrix with data points must be a numpy array!')
        if value.shape[0] != 2:
            raise ValueError('Dimensions of data-points matrix is wrong!'
                             f' There should be 2 rows (x and y) but'
                             f' there are now {value.shape[0]}.')
        if value.size == 0:
            self.__push(self.__c_init.coeffs)
            raise Empty('The data points matrix seems to be emtpy.')
        return value
