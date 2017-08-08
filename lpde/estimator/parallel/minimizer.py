from multiprocessing import Process
from queue import Empty
from numpy import zeros, square, log, ndarray, float64
from scipy.optimize import fmin_l_bfgs_b, minimize
from ..datatypes import InitialCoefficients, Signal, MinimizerParams

MINIMUM_GRADIENT = 0.1
MAXIMUM_ITERATIONS = 10000


class Minimizer(Process):
    def __init__(self, params: MinimizerParams) -> None:
        super().__init__()
        self.__params = self.__params_type_checked(params)
        self.__c_init = InitialCoefficients(self.__params.degree)
        self.__grad_c = zeros(self.__c_init.vector.size)
        self.__phi_ijn = None
        self.__control = Signal.CONTINUE
        self.__options = {'maxiter': MAXIMUM_ITERATIONS,
                          'disp': False}
        self.__constraint = {'type': 'eq',
                             'fun': self.__norm,
                             'jac': self.__grad_norm}

    def run(self):
        while self.__control != Signal.STOP:
            try:
                item_from_queue = self.__params.phi_queue.get_nowait()
                self.__phi_ijn = self.__type_and_shape_checked(item_from_queue)
            except Empty:
                pass
            else:
                self.__c_init.lagrange = self.__phi_ijn.shape[1]
                coefficients, _, status = fmin_l_bfgs_b(self.__lagrangian,
                                                        self.__c_init.vector,
                                                        self.__grad_lagrangian,
                                                        **self.__options)
                converged = self.__grad_c.dot(self.__grad_c) < MINIMUM_GRADIENT
                if (status['warnflag'] == 0) and converged:
                    self.__params.coeff_queue.put(coefficients[1:])
                else:
                    result = minimize(self.__neg_log_l, self.__c_init.coeffs,
                                      method='slsqp',
                                      jac=self.__grad_neg_log_l,
                                      constraints=self.__constraint,
                                      options=self.__options)
                    if result.success:
                        self.__params.coeff_queue.put(result.x)
            try:
                self.__control = self.__params.control.get_nowait()
            except Empty:
                self.__control = Signal.CONTINUE

    def __lagrangian(self, c: ndarray) -> float64:
        return self.__neg_log_l(c[1:]) + c[0]*self.__norm(c[1:])

    def __grad_lagrangian(self, c: ndarray) -> ndarray:
        self.__grad_c[0] = self.__norm(c[1:])
        self.__grad_c[1:] = self.__grad_neg_log_l(c[1:]) + 2.0*c[0]*c[1:]
        return self.__grad_c

    def __neg_log_l(self, c: ndarray) -> float64:
        return -log(square(c.dot(self.__phi_ijn))).sum()

    def __grad_neg_log_l(self, c: ndarray) -> ndarray:
        return float64(-2.0)*(self.__phi_ijn/c.dot(self.__phi_ijn)).sum(axis=1)

    @staticmethod
    def __norm(c: ndarray) -> float64:
        return c.dot(c) - float64(1.0)

    @staticmethod
    def __grad_norm(c: ndarray) -> ndarray:
        return 2.0 * c

    @staticmethod
    def __params_type_checked(value: MinimizerParams) -> MinimizerParams:
        if not type(value) is MinimizerParams:
            raise TypeError('Parameters must be of type <MinimizerParams>!')
        return value

    def __type_and_shape_checked(self, value: ndarray) -> ndarray:
        if not type(value) is ndarray:
            raise TypeError('Phi_ijn matrix must be a numpy array!')
        if value.shape[0] != self.__c_init.coeffs.size:
            raise ValueError('Dimensions of phi_ijn changed unexpectedly!')
        if value.size == 0:
            self.__params.coeff_queue.put(self.__c_init.coeffs)
            raise Empty('Currently, there are no data points to process.')
        return value
