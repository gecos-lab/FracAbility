from fracability import Entities
from fracability.operations import Statistics
from fracability import Plotters


fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/FracAbility/development/tests/test_data/Gozo/Set_2_clipped_DFN_test.shp', set_n=3)
boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/FracAbility/development/tests/test_data/Gozo/Interpretation_boundary_DFN_test.shp', group_n=1)
# fracture_set1 = Entities.Fractures(csv='Fractures_gozo_result.csv')
# boundary = Entities.Boundary(csv='Boundary_gozo_result.csv')
# nodes = Entities.Nodes(csv='Nodes_gozo_result.csv')
# fracture_net = Entities.FractureNetwork(csv='Fracture_net_gozo_result.csv')


fracture_set1.vtk_plot()
# boundary.vtk_plot()
# nodes.vtk_plot()

# print(fracture_net.fracture_network_to_components_df())

# fracture_net.vtk_plot()

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_boundaries(boundary)


fracture_net.calculate_topology()
fracture_net.vtk_plot()
# print(fracture_net.fracture_network_to_components_df())
# fracture_net.save_csv('gozo_result.csv')
# fracture_net.fractures.save_csv('gozo_result.csv')
# fracture_net.boundaries.save_csv('gozo_result.csv')
# fracture_net.nodes.save_csv('gozo_result.csv')

#
fitter = Statistics.NetworkFitter(fracture_net)
#
fitter.fit('lognorm')
Plotters.matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))
# # fitter.fit('expon')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('expon'))
# # fitter.fit('norm')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('norm'))
# # fitter.fit('gamma')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('gamma'))
# # fitter.fit('logistic')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('logistic'))
# fitter.fit('burr12')
# Plotters.matplot_stats_summary(fitter.get_fitted_distribution('burr12'))
# # fitter.fit('burr')
# # Plotters.matplot_stats_summary(fitter.get_fitted_distribution('burr'))
# print(fitter.get_fitted_parameters('burr12'))

