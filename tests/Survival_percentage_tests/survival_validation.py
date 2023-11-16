"""
Test survival impact using a circle -> not efficient to do many iterations... Problems related to:
1. Smaller circles have less data
2. Smaller circles have higher prob of cutting longer fractures (length bias)

We are not measuring only the impact of % censored
"""

import matplotlib.pyplot as plt
from scipy import stats as ss
import pyvista as pv
import numpy as np
from vtkmodules.vtkFiltersModeling import vtkCookieCutter

from fracability import Entities
from fracability.operations.Geometry import tidy_intersections
from fracability.operations.Statistics import NetworkFitter
from fracability.operations.Topology import nodes_conn

from numpy.random import Generator, PCG64


def lognorm_parameters(target_mean, target_std):
    """
    Get the parameters of the underlying normal distribution for mean and std of the lognorm
    :param target_mean: Target lognorm mean
    :param target_std: Target lognorm std
    """

    var_normal = np.log((target_std ** 2 / (target_mean ** 2)) + 1)

    m_normal = np.log(target_mean) - var_normal / 2

    return m_normal, np.sqrt(var_normal)


mean = 4.93
std = 6.52

mu_l, std_l = lognorm_parameters(mean, std)
distr = ss.lognorm(s=std_l, scale=np.exp(mu_l))

n_fractures = 100
seedx = 12345
seedy = 12346
seedt = 12347
numpy_randomGenx = Generator(PCG64(seedx))
numpy_randomGeny = Generator(PCG64(seedy))
numpy_randomGent = Generator(PCG64(seedt))

n_windows = 5
# theta = ss.uniform.rvs(0, 360, size=n_fractures, random_state=numpy_randomGent)
theta = 32

n_iter = 1

lengths = distr.rvs(size=n_fractures)
# lengths = ss.norm.rvs(loc=4.93, scale=6.52, size=n_fractures)
lengths[np.where(lengths < 0)] *= -1  # flip to positive negative ends
half_lengths = lengths/2

radiuses = np.linspace(0.1, max(half_lengths)*1.1, n_windows)

centers_x = ss.uniform.rvs(size=n_fractures, random_state=numpy_randomGenx)
centers_y = ss.uniform.rvs(size=n_fractures, random_state=numpy_randomGeny)

x1 = centers_x+half_lengths*np.cos(np.deg2rad(theta))
x2 = centers_x+half_lengths*np.cos(np.deg2rad((theta+180) % 360))

y1 = centers_y+half_lengths*np.sin(np.deg2rad(theta))
y2 = centers_y+half_lengths*np.sin(np.deg2rad((theta+180) % 360))

xy1 = np.vstack((x1, y1)).T

xy2 = np.vstack((x2, y2)).T

xy1 = np.insert(xy1, range(1, n_fractures+1, 1), [0, 0], axis=0)
xy2 = np.insert(xy2, range(0, n_fractures, 1), [0, 0], axis=0)

complete = xy1+xy2

xyz = np.hstack((complete, np.zeros((len(complete), 1))))
obj_center = np.mean(xyz,axis=0)

conn = np.insert(np.arange(0, len(xyz)), np.arange(0, len(xyz), 2), 2)

lines = pv.PolyData(xyz, lines=conn)
lines['RegionId'] = np.arange(0, n_fractures)

frac_net = Entities.FractureNetwork()
for r, radius in enumerate(radiuses):

    window = pv.Circle(radius, resolution=1000).translate(obj_center)
    window['RegionId'] = [r]
    boundary = Entities.Boundary(group_n=r)
    boundary.vtk_object = window
    frac_net.add_boundaries(boundary)

    cookie = vtkCookieCutter()

    cookie.SetLoopsData(window)
    cookie.SetInputData(lines)
    cookie.SetPointInterpolationToLoopEdges()
    cookie.Update()

    fractures_cut = pv.PolyData(cookie.GetOutput())
    fractures = Entities.Fractures(set_n=r)
    fractures.vtk_object = fractures_cut

    frac_net.add_fractures(fractures)

# frac_net.activate_fractures(set_n=[0])
# frac_net.activate_boundaries(group_n=[0])
#
# tidy_intersections(frac_net)
#
# nodes_conn(frac_net)  # bottleneck
#
# frac_net.vtkplot(color=['white', 'red'])

means_no_cens = []
means_cens = []
frac_censored = []

for set_n in frac_net.sets:
    print(set_n)
    frac_net.activate_fractures(set_n=[set_n])
    frac_net.activate_boundaries(group_n=[set_n])
    tidy_intersections(frac_net)
    nodes_conn(frac_net)

    fitter = NetworkFitter(frac_net, include_censoring=False)

    fitter.fit('lognorm')

    fitted_dist = fitter.get_fitted_distribution("lognorm")

    means_no_cens.append(fitted_dist.mean)

    fitter2 = NetworkFitter(frac_net, include_censoring=True)

    fitter2.fit('lognorm')

    fitted_dist2 = fitter2.get_fitted_distribution("lognorm")

    means_cens.append(fitted_dist2.mean)

    frac_censored.append(frac_net.fraction_censored)

sort = np.argsort(frac_censored)

plt.plot(np.array(frac_censored)[sort], np.array(means_no_cens)[sort], color='b', label='no censoring')
plt.plot(np.array(frac_censored)[sort], np.array(means_cens)[sort], color='r', label='censoring')
plt.hlines(distr.mean(), xmin=np.min(frac_censored), xmax=np.max(frac_censored),
                   label='distribution mean', colors='k')
plt.legend()
plt.ylim([-1, mean+std+3])
plt.show()


# no_cens_mean = np.array([])
# no_cens_std = np.array([])
#
# cens_mean = np.array([])
# cens_std = np.array([])
#
# censored_fraction = np.array([])
# radius_value = np.array([])
#
# mauldon_mean = np.array([])
#
# bounds_center = np.mean(xyz, axis=0)
#
# origin = np.array([scaled_xmin, scaled_ymin, 0])
#
# for radius in radiuses:
#     print(f'iter {i}: {radius}', end='\r')
#
#     bounds_r = np.linalg.norm(bounds_center-origin)*radius
#     radius_value = np.append(radius_value, bounds_r)
#
#     window = pv.Circle(bounds_r, resolution=1000).translate(bounds_center)
#
#     window['RegionId'] = [0]
#
#     cookie = vtkCookieCutter()
#
#     cookie.SetLoopsData(window)
#     cookie.SetInputData(lines)
#     cookie.SetPointInterpolationToLoopEdges()
#     cookie.Update()
#
#     fractures_cut = pv.PolyData(cookie.GetOutput())
#
#     fractures_1 = Entities.Fractures(set_n=1)
#
#     boundary = Entities.Boundary(group_n=1)
#
#     fractures_1.vtk_object = fractures_cut
#
#     boundary.vtk_object = window
#
#     frac_net = Entities.FractureNetwork()
#
#     frac_net.add_fractures(fractures_1)
#
#     frac_net.add_boundaries(boundary)
#
#     tidy_intersections(frac_net)
#
#     nodes_conn(frac_net)  # bottleneck
#
#     frac_net.vtkplot()
#
#     censored_fraction = np.append(censored_fraction, frac_net.fraction_censored)
#     mm = ((np.pi * bounds_r) / 2) * (frac_net.nodes.n_censored / frac_net.nodes.n_complete)
#
#     mauldon_mean = np.append(mauldon_mean, mm)
#
#     # With censoring
#
#     fitter_no_censored = NetworkFitter(frac_net, include_censoring=False)  # do not include censored lengths
#
#     fitter_no_censored.fit('norm')
#
#     fitted_dist = fitter_no_censored.get_fitted_distribution("norm")
#
#     no_cens_mean = np.append(no_cens_mean, fitted_dist.mean)
#     no_cens_std = np.append(no_cens_std, fitted_dist.std)
#
#     fitter_censored = NetworkFitter(frac_net, include_censoring=True)  # include censored lengths
#     fitter_censored.fit('norm')
#     fitted_dist = fitter_censored.get_fitted_distribution("norm")
#
#     cens_mean = np.append(cens_mean, fitted_dist.mean)
#     cens_std = np.append(cens_std, fitted_dist.std)
#
# fraction_sort = np.argsort(censored_fraction)
# iter_censored_fraction[i] = censored_fraction
# iter_no_cens_mean[i] = no_cens_mean
# iter_cens_mean[i] = cens_mean
# iter_mauldon_mean[i] = mauldon_mean
# iter_radius_value[i] = radius_value
#
# fig, axd = plt.subplot_mosaic([['A', 'B'], ['E', 'E']],
#                               constrained_layout=True)
# for i, censored_fraction in enumerate(iter_censored_fraction):
#     # axd['A'].plot(censored_fraction, iter_no_cens_mean[i], color='b', alpha=0.1)
#     # axd['A'].plot(censored_fraction, iter_cens_mean[i], color='r', alpha=0.1)
#     # axd['A'].plot(censored_fraction, iter_mauldon_mean[i], color='g', alpha=0.1)
#     axd['E'].plot(iter_radius_value[i], censored_fraction, color='k', alpha=0.1)
#
#
# mean_fraction = np.mean(iter_censored_fraction, axis=0)
# mean_no_cens_means = np.mean(iter_no_cens_mean, axis=0)
# mean_cens_means = np.mean(iter_cens_mean, axis=0)
# mean_mauldon_means = np.mean(iter_mauldon_mean, axis=0)
# mean_radius = np.mean(iter_radius_value, axis=0)
#
#
# axd['A'].set_title('Censored fraction vs mean')
# axd['A'].plot(mean_fraction, mean_no_cens_means, color='b', label='Exclude censored fractures')
# axd['A'].plot(mean_fraction, mean_cens_means, color='r', label='Include censored fractures')
# axd['A'].plot(mean_fraction, mean_mauldon_means, color='g', label='Mauldon 2002')
# axd['A'].hlines(distr.mean(), xmin=np.min(mean_fraction), xmax=np.max(mean_fraction),
#                    label='distribution mean', colors='k')
#
# axd['A'].set(xlabel='Fraction censored', ylabel='Mean')
# axd['A'].legend()
#
# axd['B'].set_title('Radius vs mean')
# axd['B'].plot(mean_radius, mean_no_cens_means, color='b', label='Exclude censored fractures')
# axd['B'].plot(mean_radius, mean_cens_means, color='r', label='Include censored fractures')
# axd['B'].hlines(distr.mean(), xmin=np.min(mean_radius), xmax=np.max(mean_radius),
#                 label='distribution mean', colors='k')
# axd['B'].set(xlabel='Radius')
# axd['B'].legend()
#
#
# axd['E'].set_title('Radius vs censored fraction')
# axd['E'].set(xlabel='Radius', ylabel='Censored fraction')
# axd['E'].plot(mean_radius, mean_fraction, color='k')
#
# plt.show()
#
# # print(np.mean(iter_censored_fraction, axis=0))

