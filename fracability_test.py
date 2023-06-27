
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Topology import nodes_conn
import fracability.Plotters as plotters
import matplotlib.pyplot as plt

from fracability.operations.Statistics import NetworkFitter
from fracability.Plotters import matplot_stats_summary



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

fractures = Entities.Fractures(fracs)

fractures_1 = Entities.Fractures(fracs_1)
fractures_2 = Entities.Fractures(fracs_2)

boundaries = Entities.Boundary(bound_gpd)

fracture_net = Entities.FractureNetwork()

fracture_net.boundaries = boundaries


fracture_net.add_fractures(fractures_1, set_number=1)
fracture_net.add_fractures(fractures_2, set_number=2)

center_object(fracture_net)

tidy_intersections(fracture_net)


# print(fracture_net.vtk_object.array_names)
#
# plotter = pv.Plotter()
#
# plotter.add_mesh(fracture_net.vtk_object,scalars='set')
# plotter.show()

nodes_conn(fracture_net)

print(fracture_net.entity_df)
# fracture_net.nodes = nodes

fracture_net.nodes.ternary_plot()

# fracture_net.matplot()

fitter = NetworkFitter(fracture_net)

# fitter.find_best_distribution()
# matplot_stats_summary(fitter)

fitter.fit('gamma')

distr = fitter.get_fit_distribution(['gamma'])

matplot_stats_summary(distr[0])
