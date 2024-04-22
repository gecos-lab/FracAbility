import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import Entities
from fracability import DATADIR
from fracability.operations import Statistics
from fracability import Plotters
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss


# Pontrelli
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1, check_geometry=False)
# fracture_set2 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_b.shp', set_n=2, check_geometry=False)
# fracture_set3 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_c.shp', set_n=3, check_geometry=False)
boundary = Entities.Boundary(shp=f'{DATADIR}/cava_pontrelli/Interpretation-boundary.shp', group_n=1)


# Salza
# fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Set_1.shp', set_n=1)
# fracture_set2 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Set_2.shp', set_n=2)
# boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/FracAbility/src/fracability/datasets/laghetto_salza/Interpretation_boundary.shp', group_n=1)


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
# fracture_net.add_fractures(fracture_set2)
# fracture_net.add_fractures(fracture_set3)

fracture_net.add_boundaries(boundary)

print('ciao')
fracture_net.calculate_topology()
vtkbackbone = fracture_net.calculate_backbone()

backbone = Entities.Fractures()
backbone.vtk_object = vtkbackbone
backbone.crs = fracture_set1.crs

# backbone.vtk_plot()
# fracture_net.save_shp('Pontrelli')
#
# backbone.save_shp('output_Pontrelli/backbone.shp')


# fracture_net.vtk_plot(markersize=6)
# fracture_net.backbone_plot()

# fracture_net.fractures.save_csv('all_fracture_out.csv')
# fracture_net.vtk_plot()
# fracture_net.ternary_plot()
# # print(fracture_net.fracture_network_to_components_df())
# fracture_net.save_csv('gozo_result.csv')
# fracture_net.fractures.save_csv('gozo_result.csv')
# # fracture_net.boundaries.save_csv('gozo_result.csv')
# # fracture_net.nodes.save_csv('gozo_result.csv')

#
# fitter_remove = Statistics.NetworkFitter(fracture_net, use_survival=False, complete_only=True)
# fitter_all = Statistics.NetworkFitter(fracture_net, use_survival=False, complete_only=False)
# fitter = Statistics.NetworkFitter(fracture_net)
#
# #
# # fitter_remove.fit('lognorm')
# # fitter_all.fit('lognorm')
# # fitter_surv.fit('lognorm')
#
# # Plotters.matplot_stats_pdf(fitter.get_fitted_distribution('lognorm'))
# fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('gengamma')
# fitter.fit('logistic')
# fitter.fit('weibull_min')
#
# print(fitter.fit_records)
# # Plotters.matplot_stats_summary(fitter_surv.get_fitted_distribution('lognorm'))
#
# Plotters.matplot_stats_uniform(fitter)
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))
# fitter.fit('gamma')
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('gamma'))
# fitter.fit('logistic')
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('logistic'))
#
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('gengamma'))
# # fitter.fit('burr')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('burr'))
# # # print(fitter.get_fitted_parameters('burr12'))



