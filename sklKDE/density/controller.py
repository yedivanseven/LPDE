from .estimator import Estimator
from ..geometry import BoundingBox
from ..producers import PRODUCER_TYPES
from ..datatypes import Kernel


class Controller:
    def __init__(self, kernel: Kernel, bounds: BoundingBox, producer) -> None:
        kernel = self.__kernel_type_checked(kernel)
        self.__bounds = self.__boundingbox_type_checked(bounds)
        producer = self.__producer_type_checked(producer)
        self.__estimator = Estimator(kernel, self.__bounds, producer)

    @property
    def is_alive(self) -> bool:
        return self.__estimator.is_alive()

    @property
    def n_points(self) -> int:
        return self.__estimator.n_points

    def start(self) -> None:
        self.__estimator.start()

    def stop(self) -> None:
        self.__estimator.stop.set()
        self.__estimator.join()

    @staticmethod
    def __kernel_type_checked(value: Kernel) -> Kernel:
        if type(value) is not Kernel:
            raise TypeError('Kernel must be of type <Kernel>!')
        return value

    @staticmethod
    def __boundingbox_type_checked(value: BoundingBox) -> BoundingBox:
        if type(value) is not BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    @staticmethod
    def __producer_type_checked(value):
        if type(value) not in PRODUCER_TYPES:
            raise TypeError('Type of producer must be in PRODUCER_TYPES!')
        return value
