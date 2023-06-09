
import geopandas as gpd

import pyvista as pv
import reliability.Reliability_testing
from matplotlib import pyplot as plt
import numpy as np
import scipy.stats as ss

from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Cleaners import connect_dots
from fracability.operations.Topology import nodes_conn
from fracability.operations.Statistics import NetworkFitter

# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'
#
# n1_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_1.shp'
# n2_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_2.shp'
#
n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'


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

nodes = fracture_net.nodes.vtk_object

nodes.set_active_scalars('node_type')


# plotter = pv.Plotter()
#
# plotter.add_mesh(fracture_net.vtk_object, color='white')
# plotter.add_mesh(nodes, render_points_as_spheres=True, point_size=8)
# plotter.show()
#
fitter = NetworkFitter(fracture_net)

data = ss.CensoredData(uncensored=fitter.complete_lengths, right=fitter.censored_lengths)

ecdf = ss.ecdf(data).cdf

fitt_list = ['lognorm',
        'norm',
        'expon',
        'gamma',
        'burr12',
        'logistic']
# data = fitter.lengths

for fitter_name in fitt_list:

    distr = getattr(ss, fitter_name)

    if fitter_name == 'normal' or fitter_name == 'logistic':
        params = distr.fit(data)
    else:
        params = distr.fit(data, floc=0)

    if len(params) == 2:
        a, b = params
        x = np.linspace(distr.ppf(0.05, a, b),
                        distr.ppf(0.995, a, b), 1000)
        cdf = distr.cdf(ecdf.quantiles, a, b)

    elif len(params) == 3:
        a, b, c = params
        x = np.linspace(distr.ppf(0.05, a, b, c),
                        distr.ppf(0.995, a, b, c), 1000)
        cdf = distr.cdf(ecdf.quantiles, a, b, c)

    test = ss.kstest(ecdf.probabilities, cdf)
    print(f'{fitter_name}: {test}')

# s = params[0]


# print(x)
#
# pdf = ss.gamma.pdf(x, s=params[0], loc=params[1], scale=params[2])
#
# cdf = ss.gamma.cdf(ecdf.quantiles, s=params[0], loc=params[1], scale=params[2])
#

# # print(ecdf)
#
# plt.step(ecdf.quantiles, ecdf.probabilities,'r')
# plt.plot(ecdf.quantiles, cdf,'b')
#
#
# plt.show()

# reliability.Reliability_testing.KStest(distribution=dist, data=fracture_net.entity_df['length'].values)

# print(fitter.accepted_fit)
# print(fitter.rejected_fit)
#
# for acc_fit in fitter.accepted_fit:
#     acc_fit.plot_function('CDF', x_max=4)
#
# for rej_fit in fitter.rejected_fit:
#     rej_fit.plot_function('CDF', x_max=4)

# fitter.fit('Fit_Lognormal_2P')
# print(fitter.get_fit_parameters())
# fitter.summary_plot(x_max=20)
# fitter.plot_function('PDF', x_max=25)
# fitter.fitter.distribution.plot('PDF')
# fitter.plot_kde()
