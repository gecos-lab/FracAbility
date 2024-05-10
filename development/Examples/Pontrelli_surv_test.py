import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import Entities
from fracability import DATADIR
import Statistics
from fracability import Plotters

# Pontrelli
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1, check_geometry=False)

boundary = Entities.Boundary(shp=f'{DATADIR}/cava_pontrelli/Interpretation-boundary.shp', group_n=1)


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)


fracture_net.add_boundaries(boundary)

fracture_net.calculate_topology()


fitter_remove = Statistics.NetworkFitter(fracture_net, use_survival=False, complete_only=True)
fitter_all = Statistics.NetworkFitter(fracture_net, use_survival=False, complete_only=False)
fitter = Statistics.NetworkFitter(fracture_net)

fitter_remove.fit('lognorm')
fitter_all.fit('lognorm')
fitter.fit('lognorm')

Plotters.matplot_stats_summary(fitter)
Plotters.matplot_stats_summary(fitter_all)
Plotters.matplot_stats_summary(fitter_remove)





