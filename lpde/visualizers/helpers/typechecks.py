from numpy import ndarray
from ...geometry import BoundingBox


def numpy_array_type_checked(value: ndarray) -> ndarray:
    if type(value) is not ndarray:
        raise TypeError('Data must be a numpy array!')
    if not len(value.shape) == 2:
        raise ValueError('Data must be a two-dimensional numpy array')
    return value


def boundingbox_type_checked(value) -> BoundingBox:
    if type(value) is not BoundingBox:
        raise TypeError('Bounds must be of type <BoundingBox>!')
    return value


def boolean_type_checked(value: bool) -> bool:
    if type(value) is not bool:
        raise TypeError('Gradient flag must be boolean, i.e., True or False!')
    return value
