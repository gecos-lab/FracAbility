
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import tidy_intersections, calculate_seg_length
from fracability.operations.Topology import nodes_conn
import matplotlib.pyplot as plt

from fracability.operations.Statistics import NetworkFitter
from fracability.Plotters import matplot_stats_summary

from scipy.stats import probplot

from fracability.examples import example_fracture_network


shp_path, _ = example_fracture_network.fracture_net_subset()


fractures_1 = Entities.Fractures(shp=shp_path['set_1'], set_n=1)
fractures_2 = Entities.Fractures(shp=shp_path['set_2'], set_n=2)

calculate_seg_length(fractures_1)

fractures_1.vtkplot(display_property='length')


boundaries = Entities.Boundary(shp=shp_path['bounds'])

fracture_net = Entities.FractureNetwork()


fracture_net.add_boundaries(boundaries)

fracture_net.add_fractures(fractures_1)
fracture_net.add_fractures(fractures_2)
# fracture_net.add_fractures(fractures)
#
# center_object(fracture_net)
#

# fracture_net.activate_fractures([1])
fracture_net.activate_fractures([2])
tidy_intersections(fracture_net)



# fracture_net.fracture_network_to_components_df().to_csv('network_example_data.csv', sep=',', index=False)

# fracture_net.plot_ternary()
#
# # fracture_net.fractures.entity_df.to_csv('data.csv', columns=['length', 'censored'])
#
# fitter = NetworkFitter(fracture_net)
# #
# fitter.find_best_distribution()
# #
# matplot_stats_summary(fitter.best_fit()['distribution'])
