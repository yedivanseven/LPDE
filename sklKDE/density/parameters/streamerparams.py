from multiprocessing.managers import DictProxy
from ...geometry import BoundingBox
from ...producers import PRODUCER_TYPES


class StreamerParams:
    def __init__(self, bounds: BoundingBox, producer, data: DictProxy) -> None:
        self.__bounds = self.__boundingbox_type_checked(bounds)
        self.__producer = self.__producer_type_checked(producer)
        self.__data = self.__managed_dict_type_checked(data)

    @property
    def bounds(self) -> BoundingBox:
        return self.__bounds

    @property
    def producer(self):
        return self.__producer

    @property
    def data(self) -> DictProxy:
        return self.__data

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

    @staticmethod
    def __managed_dict_type_checked(value: DictProxy) -> DictProxy:
        if type(value) is not DictProxy:
            raise TypeError('Data must be of type <DictProxy>!')
        return value
