from multiprocessing.managers import DictProxy
from .densityparams import DensityParams
from ...datatypes import Kernel
from ...geometry import BoundingBox, Grid


class ControllerParams:
    def __init__(self, params: DensityParams, data: DictProxy) -> None:
        self.__params = self.__density_params_type_checked(params)
        self.__data = self.__managed_dict_type_checked(data)

    @property
    def kernel(self) -> Kernel:
        return self.__params.kernel

    @property
    def bounds(self) -> BoundingBox:
        return self.__params.bounds

    @property
    def grid(self) -> Grid:
        return self.__params.grid

    @property
    def producer(self):
        return self.__params.producer

    @property
    def data(self) -> DictProxy:
        return self.__data

    @staticmethod
    def __density_params_type_checked(value: DensityParams) -> DensityParams:
        if type(value) is not DensityParams:
            raise TypeError('Parameters must be of type <DensityParams>!')
        return value

    @staticmethod
    def __managed_dict_type_checked(value: DictProxy) -> DictProxy:
        if type(value) is not DictProxy:
            raise TypeError('Type of data be multiprocessing <DictProxy>!')
        return value
