from multiprocessing import Process
from queue import Empty
from numpy import frombuffer
from time import sleep
from ..datatypes import SmootherParams


class Smoother(Process):
    def __init__(self, params: SmootherParams) -> None:
        super().__init__()
        self.__params = self.__type_checked(params)
        self.__control = 'continue'
        self.__initial = frombuffer(self.__params.smoothed.get_obj()).copy()

    def run(self):
        smooth = self.__initial.copy()
        while self.__control != 'stop':
            try:
                raw = self.__params.coefficients.get_nowait()
            except Empty:
                raw = self.__initial
            smooth = self.__params.damp*raw + (1.0-self.__params.damp)*smooth
            sleep(self.__params.timestep)
            self.__params.smoothed.get_obj()[:] = smooth
            try:
                self.__control = self.__params.control.get_nowait()
            except Empty:
                self.__control = 'continue'

    @staticmethod
    def __type_checked(value: SmootherParams) -> SmootherParams:
        if not type(value) is SmootherParams:
            raise TypeError('Parameters must be of type <SmootherParams>!')
        return value
