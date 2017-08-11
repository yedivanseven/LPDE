from ..estimators.datatypes import SmootherParams, Signal
from ..estimators.parallel.smoother import Smoother


class SmootherController:
    def __init__(self, smoother: Smoother, params: SmootherParams) -> None:
        self.__smoother = self.__smoother_type_checked(smoother)
        self.__params = self.__params_type_checked(params)

    def stop(self):
        if not self.__params.control._closed:
            self.__params.control.put(Signal.STOP)
            self.__params.control.close()
            self.__params.control.join_thread()
        if not self.__params.coeff_queue._closed:
            self.__params.coeff_queue.close()
            self.__params.coeff_queue.join_thread()
        if self.__smoother.is_alive():
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
