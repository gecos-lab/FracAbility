
import geopandas as gpd
from matplotlib import pyplot as plt
import pyvista as pv
import networkx as nx
from ast import literal_eval
import numpy as np

from fracability import Entities
from fracability.Operations import tidy_intersections, nodes_conn

n_path = 'fracability/datasets/Fracture_network_test4.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'
# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'


frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

fractures = Entities.Fractures(frac_gpd)
boundaries = Entities.Boundary(bound_gpd)


fracture_net = Entities.FractureNetwork()
#
fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)
#
fracture_net.center_object()
tidy_intersections(fracture_net)




# tidy_frac_net = Entities.FractureNetwork(tidy_gdf)
#
# print(tidy_frac_net.fractures)

graph = fracture_net.get_network_output()
class_id, class_names = nodes_conn(graph, fracture_net)

print(graph.adj)
#
# #
fractures_nodes = fracture_net.get_nodes()

fractures_nodes['class_id'] = class_id
#
fractures_nodes = fractures_nodes.extract_points(fractures_nodes['class_id'] >=0)


plotter = pv.Plotter()

plotter.add_mesh(fracture_net.get_vtk_output(), color='white')
plotter.add_mesh(fractures_nodes, render_points_as_spheres=True, point_size=5)
plotter.view_xy()
plotter.show()
