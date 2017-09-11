from ...datatypes import Kernel
from ...geometry import BoundingBox, Grid
from ...producers import PRODUCER_TYPES


class DensityParams:
    def __init__(self, kernel: Kernel, bounds: BoundingBox,
                 grid: Grid, producer) -> None:
        self.__kernel = self.__kernel_type_checked(kernel)
        self.__bounds = self.__boundingbox_type_checked(bounds)
        self.__producer = self.__producer_type_checked(producer)
        self.__grid = self.__grid_type_checked(grid)

    @property
    def kernel(self) -> Kernel:
        return self.__kernel

    @property
    def bounds(self) -> BoundingBox:
        return self.__bounds

    @property
    def grid(self) -> Grid:
        return self.__grid

    @property
    def producer(self):
        return self.__producer

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
    def __grid_type_checked(value: Grid) -> Grid:
        if type(value) is not Grid:
            raise TypeError('Grid must be of type <Grid>!')
        return value

    @staticmethod
    def __producer_type_checked(value):
        if type(value) not in PRODUCER_TYPES:
            raise TypeError('Type of producer must be in PRODUCER_TYPES!')
        return value
