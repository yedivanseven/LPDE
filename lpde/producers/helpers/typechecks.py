from ...geometry import BoundingBox


def boundingbox_type_checked(value) -> BoundingBox:
    if type(value) is not BoundingBox:
        raise TypeError('Bounds must be of type <BoundingBox>!')
    return value
