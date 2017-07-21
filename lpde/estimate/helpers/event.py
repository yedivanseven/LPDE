from uuid import UUID
from ...geometry import PointAt


class Event:
    def __init__(self, uuid: UUID, add: bool, location: PointAt =None) -> None:
        self.__uuid = self.__uuid_type_checked(uuid)
        self.__add = self.__bool_type_checked(add)
        self.__location = self.__point_type_checked(location)
        if self.__add and not self.__location:
            raise ValueError('If an event is added, it must have a location!')

    @property
    def id(self) -> UUID:
        return self.__uuid

    @property
    def add(self) -> bool:
        return self.__add

    @property
    def location(self) -> PointAt:
        return self.__location

    @staticmethod
    def __uuid_type_checked(uuid: UUID) -> UUID:
        if not type(uuid) is UUID:
            raise TypeError('Uuid must be of type <UUID>!')
        return uuid

    @staticmethod
    def __bool_type_checked(add: bool) -> bool:
        if not type(add) is bool:
            raise TypeError('Add must be boolean!')
        return add

    @staticmethod
    def __point_type_checked(location: PointAt) -> PointAt:
        if location is None:
            return location
        if not type(location) is PointAt:
            raise TypeError('Location must be of type <PointAt>!')
        return location

