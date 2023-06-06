
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Cleaners import connect_dots
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


center_object(fracture_net)


tidy_intersections(fracture_net)
connect_dots(fracture_net)


# backbone = find_backbone(fracture_net)

nodes_conn(fracture_net)

# nodes = fracture_net.nodes.vtk_object
#
# nodes.set_active_scalars('class_id')


# plotter = pv.Plotter()
#
# plotter.add_mesh(fracture_net.vtk_object, color='white')
# plotter.add_mesh(nodes, render_points_as_spheres=True)
# plotter.show()


fitter = NetworkFitter(fracture_net)


fitter.find_best_distribution()

for acc_fit in fitter.accepted_fit:
    acc_fit.summary_plot(x_max=4)

for rej_fit in fitter.rejected_fit:
    rej_fit.summary_plot(x_max=4)

# fitter.fit('Fit_Lognormal_2P')
# print(fitter.get_fit_parameters())
# fitter.summary_plot(x_max=20)
# fitter.plot_function('PDF', x_max=25)
# fitter.fitter.distribution.plot('PDF')
# fitter.plot_kde()
