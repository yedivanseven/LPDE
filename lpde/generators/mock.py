from ..geometry import BoundingBox

class MockParams:
    def __init__(self, rate: float, burn_in: int, n_events: int,
                 bounds: BoundingBox, dist: function) -> None:
        self.__rate = self.__float_type_and_range_checked(rate)
        self.__burn = self.__integer_type_and_range_checked(burn_in)
        self.__n = self.__integer_type_and_range_checked(n_events)
        self.__bounds = self.__bounds_type_checked(bounds)
        self.__dist = self.__function_type_checked(dist)


class MockGenerator:
    def __init__(self, params: MockParams) -> None:
        self.__params = self.__params_type_checked(params)


