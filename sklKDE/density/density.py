from .controller import Controller
from ..datatypes import Kernel
from ..geometry import BoundingBox
from ..producers import PRODUCER_TYPES


class Density:
    def __init__(self, kernel: Kernel, bounds: BoundingBox, producer) -> None:
        kernel = self.__kernel_type_checked(kernel)
        self.__bounds = self.__boundingbox_type_checked(bounds)
        producer = self.__producer_type_checked(producer)
        self.__controller = Controller(kernel, self.__bounds, producer)

    @property
    def control(self) -> Controller:
        return self.__controller

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
