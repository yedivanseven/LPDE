from numpy import seterr
from uuid import uuid4

from lpde.geometry import WidthOf, Window, PointAt, BoundingBox, Mapper, Grid
from lpde.estimators import ParallelEstimator
from lpde.estimators.datatypes import Event, Degree, Action
from lpde.producers import MockParams
from lpde.producers.distributions import gaussian
from lpde.visualizers import Visualize


_ = seterr(over='ignore')


legendre_width = WidthOf(1.8)

center = PointAt(51.375, 35.675)
window = Window(0.55, 0.35)
bounds = BoundingBox(center, window)

mapper = Mapper(bounds, legendre_width)

degree = Degree(20, 20)
params = MockParams(30, 1000, gaussian)
demand = ParallelEstimator(degree, mapper, params)


demand.controller.start(1, 1.0)

print('Producer:', demand.controller.producer.pid)
print('Transformer:', demand.controller.transformer.pid)
print('Minimizer:', demand.controller.minimizers[0].pid)
print('Smoother:', demand.controller.smoother.pid)
