from numpy.random import multivariate_normal as mv_norm
from .helpers.typechecks import boundingbox_type_checked
from ..geometry import PointAt, BoundingBox


def gaussian(bounds: BoundingBox) -> PointAt:
    bounds = boundingbox_type_checked(bounds)
    sigma_x = (bounds.window[0]/10.0)**2
    sigma_y = (bounds.window[1]/10.0)**2
    x, y = mv_norm(bounds.center, ((sigma_x, 0), (0, sigma_y)))
    candidate = PointAt(x, y)
    return candidate if bounds.contain(candidate) else gaussian(bounds)
