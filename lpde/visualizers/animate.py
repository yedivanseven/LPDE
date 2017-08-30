from numpy import ndarray
from .basic import basic
from .helpers.typechecks import numpy_array_type_checked
from .helpers.typechecks import boundingbox_type_checked
from .helpers.typechecks import boolean_type_checked
from ..geometry import BoundingBox

render_function_for = {False: basic,
                       True: None} #onmap}


def animate(data: ndarray, bounds: BoundingBox, cartopy: bool =False) -> None:
    data = numpy_array_type_checked(data)
    bounds = boundingbox_type_checked(bounds)
    cartopy = boolean_type_checked(cartopy)
    # TODO: Remove this if ... then ... once this feature is implemented
    if cartopy:
        raise NotImplementedError('Cartopy support is not implemented yet!')
    render = render_function_for[cartopy]
    render(data, bounds)


