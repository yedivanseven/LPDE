from numpy.random import multivariate_normal as mv_norm
from ...geometry import PointAt, BoundingBox


def bbox_type_checked(value) -> BoundingBox:
    if not type(value) is BoundingBox:
        raise TypeError('Bounds must be of type <BoundingBox>!')
    return value


def gaussian(bounds: BoundingBox) -> PointAt:
    bounds = bbox_type_checked(bounds)
    sigma_x = bounds.window[0]/20.0
    sigma_y = bounds.window[1]/20.0
    x, y = mv_norm(bounds.center, ((sigma_x, 0), (0, sigma_y)))
    candidate = PointAt(x, y)
    return candidate if bounds.contain(candidate) else gaussian(bounds)
