from ..estimator.datatypes import SmootherParams, Signal
from ..estimator.parallel.smoother import Smoother


class SmootherController:
    def __init__(self, smoother: Smoother, params: SmootherParams) -> None:
        self.__smoother = self.__smoother_type_checked(smoother)
        self.__params = self.__params_type_checked(params)

    def stop(self):
        self.__params.control.put(Signal.STOP)
        self.__params.control.close()
        self.__params.control.join_thread()
        self.__params.coefficients.close()
        self.__params.coefficients.join_thread()
        self.__smoother.join()

    @staticmethod
    def __smoother_type_checked(value: Smoother) -> Smoother:
        if not type(value) is Smoother:
            raise TypeError('Smoother must be of type <Smoother>!')
        return value

    @staticmethod
    def __params_type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value
