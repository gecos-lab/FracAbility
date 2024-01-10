from fracability import Entities
from fracability.operations import Statistics
from fracability import Plotters
import geopandas as gpd

boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/Progetti/github/FracAbility/development/Spacing/data/cava_pontrelli/Interpretation-boundary.shp', group_n=1)

df = gpd.read_file('/home/gabriele/STORAGE/Progetti/github/FracAbility/development/Spacing/data/cava_pontrelli/FN_set_1.shp')

df_faults = df.loc[df['Fault'] == 1]
df_joints = df.loc[df['Fault'] == 0]
fracture_set1 = Entities.Fractures(df_faults, set_n=1)
fracture_set2 = Entities.Fractures(df_joints, set_n=2)

# fracture_set1 = Entities.Fractures(shp='fracability/datasets/example_fracture_network_data/shp/Set_1.shp', set_n=1)
# fracture_set2 = Entities.Fractures(shp='fracability/datasets/example_fracture_network_data/shp/Set_2.shp', set_n=2)
# boundary = Entities.Boundary(shp='fracability/datasets/example_fracture_network_data/shp/Interpretation_boundary_laghettoSalza.shp', group_n=1)

# fracture_set1 = Entities.Fractures(csv='Fractures_gozo_result.csv')
# boundary = Entities.Boundary(csv='Boundary_gozo_result.csv')
# nodes = Entities.Nodes(csv='Nodes_gozo_result.csv')
# fracture_net = Entities.FractureNetwork(csv='Fracture_net_gozo_result.csv')


# fracture_set1.vtk_plot()
# boundary.vtk_plot()
# nodes.vtk_plot()

# print(fracture_net.fracture_network_to_components_df())

# fracture_net.vtk_plot()

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)
fracture_net.add_boundaries(boundary)


# fracture_net.deactivate_fractures(set_n=[2])
fracture_net.calculate_topology()
print(fracture_net.fraction_censored)
# fracture_net.vtk_plot()
# fracture_net.save_shp('/home/gabriele/Desktop/s1.shp')
# print(fracture_net.fracture_network_to_components_df())
# fracture_net.save_csv('gozo_result.csv')
# fracture_net.fractures.save_csv('gozo_result.csv')
# fracture_net.boundaries.save_csv('gozo_result.csv')
# fracture_net.nodes.save_csv('gozo_result.csv')

#
fitter = Statistics.NetworkFitter(fracture_net, include_censoring=True)

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

