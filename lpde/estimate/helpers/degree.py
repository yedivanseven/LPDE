from collections import namedtuple

DegreeBase = namedtuple('Degree', ['k_max', 'l_max'])


class Degree(DegreeBase):
    def __new__(cls, k_max: int, l_max: int) -> DegreeBase:
        k_max = cls.__type_and_range_checked(k_max)
        l_max = cls.__type_and_range_checked(l_max)
        self = super().__new__(cls, k_max, l_max)
        return self

    __slots__ = ()

    @staticmethod
    def __type_and_range_checked(value: int) -> int:
        if not type(value) is int:
            raise TypeError('Maximum polynomial degree must be an integer!')
        if value < 0:
            raise ValueError('Maximum polynomial degree must not be negative!')
        return value


if __name__ == '__main__':
    degree = Degree(10, 10)
    print(degree)
    print(degree.k_max)
    print(degree.l_max)
