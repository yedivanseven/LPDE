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
        if type(value) is not UUID:
            raise TypeError('Uuid must be of type <UUID>!')
        return value

    @staticmethod
    def __action_type_checked(value: Action) -> Action:
        if type(value) is not Action:
            raise TypeError('Action must be of type <Action>!')
        return value

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        # This is a bit awkward but necessary to satisfy type checking.
        if value is not None:
            if type(value) is not PointAt:
                raise TypeError('Location must be of type <PointAt>!')
        return value


if __name__ == '__main__':
    from uuid import uuid4

    point = PointAt(1, 2)
    event = Event(uuid4(), Action.ADD, point)
    print(event.location.position)
    print(event.action)
    print(event.id)
