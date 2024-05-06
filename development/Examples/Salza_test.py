import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import Entities
from fracability import DATADIR
from fracability.operations import Statistics
from fracability import Plotters



# Salza
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/laghetto_salza/Set_1.shp', set_n=1)
fracture_set2 = Entities.Fractures(shp=f'{DATADIR}/laghetto_salza/Set_2.shp', set_n=2)
boundary = Entities.Boundary(shp=f'{DATADIR}/laghetto_salza/Interpretation_boundary.shp', group_n=1)


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)

fracture_net.add_boundaries(boundary)

# print('ciao')
fracture_net.calculate_topology()

# fracture_net.save_shp('Salza')
fracture_net.deactivate_fractures([2])
fracture_net.fractures.save_csv('Salza')

# fitter = Statistics.NetworkFitter(fracture_net)
#
# fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('gengamma')
# fitter.fit('logistic')
# fitter.fit('weibull_min')
#
# Plotters.matplot_stats_table(fitter)
# # Plotters.matplot_stats_uniform(fitter)
# # Plotters.matplot_stats_ranks(fitter)
#
fracture_net.deactivate_fractures([1])
fracture_net.fractures.save_csv('Salza')
# fitter = Statistics.NetworkFitter(fracture_net)
#
# fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('gengamma')
# fitter.fit('logistic')
# fitter.fit('weibull_min')
#
# Plotters.matplot_stats_table(fitter)
# # Plotters.matplot_stats_uniform(fitter)
# # Plotters.matplot_stats_ranks(fitter)
