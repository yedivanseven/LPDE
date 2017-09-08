from numpy import float64

VALID_KERNEL_NAMES = ('gaussian',
                      'tophat')


class Kernel:
    def __init__(self, name: str, bandwidth: float) -> None:
        self.__name = self.__valid_name_checked(name)
        self.__bandwidth = self.__numeric_type_and_range_checked(bandwidth)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def bandwidth(self) -> float:
        return self.__bandwidth

    @staticmethod
    def __valid_name_checked(value: str) -> str:
        if type(value) is not str:
            raise TypeError('The kernel name must be a string!')
        if value not in VALID_KERNEL_NAMES:
            raise ValueError(f'Kernel must be one of {VALID_KERNEL_NAMES}!')
        return value

    @staticmethod
    def __numeric_type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Kernel bandwidth must be a number!')
        if not value > 0:
            raise ValueError('Kernel bandwidth must be > 0!')
        return float(value)
