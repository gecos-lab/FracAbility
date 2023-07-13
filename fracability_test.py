
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Topology import nodes_conn
import matplotlib.pyplot as plt

from fracability.operations.Statistics import NetworkFitter
from fracability.Plotters import matplot_stats_summary

from scipy.stats import probplot


# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'
#
n1_path = 'fracability/datasets/Set_1.shp'
n2_path = 'fracability/datasets/Set_2.shp'
#
n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'

fracs = gpd.read_file(n_path)

fracs_1 = gpd.read_file(n1_path)
fracs_2 = gpd.read_file(n2_path)

bound_gpd = gpd.read_file(b_path)

fractures = Entities.Fractures(fracs, 1)


fractures_1 = Entities.Fractures(fracs_1, 1)
fractures_2 = Entities.Fractures(fracs_2, 2)

boundaries = Entities.Boundary(bound_gpd)

fracture_net = Entities.FractureNetwork()


fracture_net.add_boundaries(boundaries)

fracture_net.add_fractures(fractures_1)
fracture_net.add_fractures(fractures_2)
# fracture_net.add_fractures(fractures)
#
center_object(fracture_net)
#

# fracture_net.activate_fractures([1])

tidy_intersections(fracture_net)

nodes_conn(fracture_net)

fracture_net.fracture_network_to_components_df().to_csv('network.csv', sep=',', index=False)

# fracture_net.plot_ternary()

# fracture_net.fractures.entity_df.to_csv('data.csv', columns=['length', 'censored'])

fitter = NetworkFitter(fracture_net)
#
# fitter.find_best_distribution()
#
matplot_stats_summary(fitter.best_fit()['distribution'])
#
# pv.Report()