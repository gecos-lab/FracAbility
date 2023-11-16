import matplotlib.pyplot as plt
from vtkmodules.vtkFiltersModeling import vtkCookieCutter

from fracability import Entities
from fracability.operations.Geometry import tidy_intersections
from fracability.operations.Statistics import NetworkFitter
from fracability.operations.Topology import nodes_conn

from fracability.examples import example_fracture_network

import geopandas as gpd
import numpy as np
import pyvista as pv

shp_path, _ = example_fracture_network.fracture_net()


cava_set1 = '/home/gabriele/STORAGE/projects/FracAbility/fracability/datasets/cava_pontrelli/FN_set_1.shp'
cava_bounary = '/home/gabriele/STORAGE/projects/FracAbility/fracability/datasets/cava_pontrelli/Interpretation-boundary.shp'

cava_boundary_shp = gpd.read_file(cava_bounary)

minx, miny, maxx, maxy = cava_boundary_shp['geometry'].bounds.values[0]
bounds_center = np.array(cava_boundary_shp['geometry'].centroid.values[0].xy)
bounds_center = np.append(bounds_center, [0.0])
# set_1 = shp_path['set_1']
# set_2 = shp_path['set_2']


fractures_1 = Entities.Fractures(shp=cava_set1, set_n=1)

vtk_frac = fractures_1.vtk_object
vtk_frac.translate(-np.array(vtk_frac.center), transform_all_input_vectors=True, inplace=True)

scales = np.arange(0.1, 1, 0.1)

fracture_net = Entities.FractureNetwork()

for i, scale in enumerate(scales):
    bounds_r = np.linalg.norm(bounds_center - [minx, miny, 0]) * scale
    window = pv.Circle(bounds_r, resolution=1000)

    window['RegionId'] = np.array([i+1])

    cookie = vtkCookieCutter()

    cookie.SetLoopsData(window)
    cookie.SetInputData(vtk_frac)
    cookie.SetPointInterpolationToLoopEdges()
    cookie.Update()

    fractures_cut = pv.PolyData(cookie.GetOutput())

    fractures = Entities.Fractures(set_n=i + 1)
    fractures.vtk_object = fractures_cut

    fracture_net.add_fractures(fractures)

    boundary = Entities.Boundary(group_n=i + 1)
    boundary.vtk_object = window

    fracture_net.add_boundaries(boundary)

means_no_cens = []
means_cens = []
frac_censored = []

for set_n in fracture_net.sets:
    fracture_net.activate_fractures(set_n=[set_n])
    fracture_net.activate_boundaries(group_n=[set_n])
    tidy_intersections(fracture_net)
    nodes_conn(fracture_net)

    fitter = NetworkFitter(fracture_net, include_censoring=False)

    fitter.fit('lognorm')

    fitted_dist = fitter.get_fitted_distribution("lognorm")

    means_no_cens.append(fitted_dist.mean)

    fitter2 = NetworkFitter(fracture_net, include_censoring=True)

    fitter2.fit('lognorm')

    fitted_dist2 = fitter2.get_fitted_distribution("lognorm")

    means_cens.append(fitted_dist2.mean)

    frac_censored.append(fracture_net.fraction_censored)


sort = np.argsort(frac_censored)

plt.plot(np.array(frac_censored)[sort], np.array(means_no_cens)[sort], color='b')
plt.plot(np.array(frac_censored)[sort], np.array(means_cens)[sort], color='r')

plt.show()