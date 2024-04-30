import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import Entities
from fracability import DATADIR
from fracability.operations import Statistics
from fracability import Plotters


# Pontrelli
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1, check_geometry=False)
boundary = Entities.Boundary(shp=f'{DATADIR}/cava_pontrelli/Interpretation-boundary.shp', group_n=1)


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)

fracture_net.add_boundaries(boundary)

fracture_net.calculate_topology()


# fracture_net.save_shp('Pontrelli')
fracture_net.fractures.save_csv('Pontrelli')


fitter = Statistics.NetworkFitter(fracture_net)

fitter.fit('lognorm')
fitter.fit('expon')
fitter.fit('norm')
fitter.fit('gamma')
fitter.fit('gengamma')
fitter.fit('logistic')
fitter.fit('weibull_min')


Plotters.matplot_stats_table(fitter)
# Plotters.matplot_stats_uniform(fitter)
# Plotters.matplot_stats_ranks(fitter)




