from multiprocessing.managers import DictProxy
from ...datatypes import Kernel
from ...geometry import Grid, BoundingBox


class GridMapperParams:
    def __init__(self, kernel: Kernel, bounds: BoundingBox,
                 grid: Grid, data: DictProxy) -> None:
        self.__kernel = self.__kernel_type_checked(kernel)
        self.__bounds = self.__boundingbox_type_checked(bounds)
        self.__grid = self.__grid_type_checked(grid)
        self.__data = self.__managed_dict_type_checked(data)

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
    def data(self) -> DictProxy:
        return self.__data

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
    def __managed_dict_type_checked(value: DictProxy) -> DictProxy:
        if type(value) is not DictProxy:
            raise TypeError('Data must be of type <DictProxy>!')
        return value
