from uuid import UUID
from .action import Action
from ...geometry import PointAt


class Event:
    def __init__(self, uuid: UUID, action: Action, location: PointAt =None):
        self.__uuid = self.__uuid_type_checked(uuid)
        self.__action = self.__action_type_checked(action)
        self.__location = self.__point_type_checked(location)
        if self.__action in (Action.ADD, Action.MOVE) and not self.__location:
            err_msg = 'If an ID is added or moved, it must have a location!'
            raise ValueError(err_msg)

    @property
    def id(self) -> UUID:
        return self.__uuid

    @property
    def action(self) -> Action:
        return self.__action

    @property
    def location(self) -> PointAt:
        return self.__location

    @staticmethod
    def __uuid_type_checked(value: UUID) -> UUID:
        if not type(value) is UUID:
            raise TypeError('Uuid must be of type <UUID>!')
        return value

    @staticmethod
    def __action_type_checked(value: Action) -> Action:
        if not type(value) is Action:
            raise TypeError('Action must be of type <Action>!')
        return value

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if value is None:
            return value
        if not type(value) is PointAt:
            raise TypeError('Location must be of type <PointAt>!')
        return value

