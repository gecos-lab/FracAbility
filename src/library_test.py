from fracability import Entities
from fracability.operations import Statistics
from fracability import Plotters
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
# fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_BR_03B/Fracture_network_1.shp', set_n=1)
#
# fracture_set2 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_BR_03B/Fracture_network_2_4.shp', set_n=2)
#
# fracture_set3 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_BRdotto_03B/Fracture_network_3.shp', set_n=3)
#
#
# boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_BR_03B/Interpretation_boundary.shp', group_n=1)


# fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/cava_pontrelli/FN_set_1.shp', set_n=1)
# boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/cava_pontrelli/Interpretation-boundary.shp', group_n=1)


fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Set_1.shp', set_n=1)
fracture_set2 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Set_2.shp', set_n=2)
boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Interpretation_boundary.shp', group_n=1)

# fracture_set1 = Entities.Fractures(csv='Fractures_gozo_result.csv')
# boundary = Entities.Boundary(csv='Boundary_gozo_result.csv')
# nodes = Entities.Nodes(csv='Nodes_gozo_result.csv')


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)
# fracture_net.add_fractures(fracture_set3)

fracture_net.add_boundaries(boundary)

# fracture_net.check_network()

#
#
# fracture_net.deactivate_fractures([1])
fracture_net.calculate_topology()

# fracture_net.vtk_plot()
fracture_net.fractures.save_csv('all_fracture_out.csv')
# fracture_net.vtk_plot()
# fracture_net.ternary_plot()
# # print(fracture_net.fracture_network_to_components_df())
# # fracture_net.save_csv('gozo_result.csv')
# # fracture_net.fractures.save_csv('gozo_result.csv')
# # fracture_net.boundaries.save_csv('gozo_result.csv')
# # fracture_net.nodes.save_csv('gozo_result.csv')

#
fitter = Statistics.NetworkFitter(fracture_net, use_survival=True, complete_only=True)
# #
fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('gengamma')
# fitter.fit('logistic')
# fitter.fit('weibull_min')
Plotters.matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))

# Plotters.matplot_stats_uniform(fitter)
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('norm'))
# fitter.fit('gamma')
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('gamma'))
# fitter.fit('logistic')
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('logistic'))
#
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('gengamma'))
# # fitter.fit('burr')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('burr'))
# # # print(fitter.get_fitted_parameters('burr12'))
#
print(fitter.fit_records)


