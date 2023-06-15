
import geopandas as gpd

import pyvista as pv
import reliability.Reliability_testing
from matplotlib import pyplot as plt
import numpy as np
import scipy.stats as ss

from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Topology import nodes_conn
from fracability.operations.Statistics import NetworkFitter


n_path = 'fracability/datasets/frac_pesce.shp'
b_path = 'fracability/datasets/grid_pesce.shp'
#
# n1_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_1.shp'
# n2_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_2.shp'
#
# n_path = 'fracability/datasets/Fracture_network.shp'
# b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'


fracs = gpd.read_file(n_path)

bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fractures = Entities.Fractures(fracs)

boundaries = Entities.Boundary(bound_gpd)

# clean_dup_points(fractures)

fracture_net = Entities.FractureNetwork()


fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)
# print(fracture_net.vtk_object.plot())


center_object(fracture_net)


tidy_intersections(fracture_net)


nodes = nodes_conn(fracture_net)
print('ciao')
# print(fracture_net.entity_df)
#
# nodes = fracture_net.nodes.vtk_object

nodes.vtk_object.set_active_scalars('node_type')
print('ciao')

plotter = pv.Plotter()

# plotter.add_mesh(fracture_net.boundaries.vtk_object, color='red')
plotter.add_mesh(fracture_net.vtk_object, color='white')

plotter.add_mesh(nodes.vtk_object, render_points_as_spheres=True, point_size=8)
print('ciao')
# plotter.add_mesh(fractures.vtk_object.points, render_points_as_spheres=True, point_size=8)
plotter.show()
#

# fitter = NetworkFitter(fracture_net)
#
# # fitter.fit('lognorm')
# # fitter.fit('norm')
# # fitter.fit('weibull_min')
# # fitter.fit('exponnorm')
#
# # print(fitter.fit_records)
#
# best_fit = fitter.find_best_distribution()
#
# print(best_fit)

