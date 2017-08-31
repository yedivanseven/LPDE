from numpy.random import multivariate_normal as mv_norm
from ..geometry import PointAt, BoundingBox


def boundingbox_type_checked(value) -> BoundingBox:
    if type(value) is not BoundingBox:
        raise TypeError('Bounds must be of type <BoundingBox>!')
    return value


def gaussian(bounds: BoundingBox) -> PointAt:
    bounds = boundingbox_type_checked(bounds)
    sigma_x = (bounds.window[0]/10.0)**2
    sigma_y = (bounds.window[1]/10.0)**2
    x, y = mv_norm(bounds.center, ((sigma_x, 0), (0, sigma_y)))
    candidate = PointAt(x, y)
    return candidate if bounds.contain(candidate) else gaussian(bounds)
