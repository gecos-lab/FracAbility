"""
Test survival impact using circular windows  Here we try to fix
survival_validation problems by generating for each window n_fractures based on the same distribution but I don't think
this is a correct approach. -> extremely slow to do...

"""


import matplotlib.pyplot as plt
import pyvista as pv
import scipy.stats as ss
import numpy as np
from vtkmodules.vtkFiltersModeling import vtkCookieCutter

from fracability import Entities
from fracability.operations.Geometry import tidy_intersections
from fracability.operations.Statistics import NetworkFitter
from fracability.operations.Topology import nodes_conn


p1 = np.array([636956.8988181990571320, 4518449.8742292737588286, 0])
p2 = np.array([637087.6015316098928452, 4518609.1086281584575772, 0])

max_R = np.linalg.norm(p1-p2)/2
n_frac = 1600

params = (1.004836094520663, 0, 2.9804836275787645)
distr = ss.lognorm(*params)
radiuses = np.linspace(distr.mean(), max_R, 10)

fracture_network = Entities.FractureNetwork()


for i, R in enumerate(radiuses):

    gen_R = R*np.sin(np.rad2deg(45))
    lengths = ss.lognorm.rvs(*params, n_frac)

    r = gen_R * np.sqrt(np.random.uniform(size=n_frac))
    theta = np.random.uniform(size=n_frac) * 2 * np.pi
    frac_dir = np.random.uniform(0,360, size=1)

    x = r*np.sin(theta)
    y = r*np.cos(theta)
    z = r*0

    # print(lengths)
    # sns.lineplot(x=lengths, y=distr.cdf(lengths), color='r')
    # plt.show()

    half_lengths = lengths/2

    xyz = np.column_stack((x, y, z))

    xyz1 = xyz.copy()
    xyz2 = xyz.copy()

    xyz1[:, 0] = xyz[:, 0] + half_lengths*np.cos(np.deg2rad(frac_dir))
    xyz2[:, 0] = xyz[:, 0] + half_lengths*np.cos(np.deg2rad((frac_dir+180) % 360))

    xyz1[:, 1] = xyz[:, 1] + half_lengths*np.sin(np.deg2rad(frac_dir))
    xyz2[:, 1] = xyz[:, 1] + half_lengths*np.sin(np.deg2rad((frac_dir+180) % 360))

    xyz_complete = np.array([[i, j] for i, j in zip(xyz1, xyz2)]).reshape(-1, 3)
    conn = np.insert(np.arange(0, len(xyz_complete)), np.arange(0, len(xyz_complete), 2), 2)
    lines = pv.PolyData(xyz_complete, lines=conn)
    lines['RegionId'] = np.arange(0, n_frac)
    window = pv.Circle(radius=R)
    window['RegionId'] = [i+1]

    cookie = vtkCookieCutter()

    cookie.SetLoopsData(window)
    cookie.SetInputData(lines)
    cookie.SetPointInterpolationToLoopEdges()
    cookie.Update()

    fractures_cut = pv.PolyData(cookie.GetOutput())
    fractures = Entities.Fractures(set_n=i + 1)
    fractures.vtk_object = fractures_cut

    fracture_network.add_fractures(fractures)

    boundary = Entities.Boundary(group_n=i + 1)
    boundary.vtk_object = window
    fracture_network.add_boundaries(boundary)

means_no_cens = []
means_cens = []
frac_censored = []


for set_n in fracture_network.sets:
    print(set_n)
    fracture_network.activate_fractures(set_n=[set_n])
    fracture_network.activate_boundaries(group_n=[set_n])
    tidy_intersections(fracture_network)
    nodes_conn(fracture_network)

    fitter = NetworkFitter(fracture_network, include_censoring=False)

    fitter.fit('lognorm')

    fitted_dist = fitter.get_fitted_distribution("lognorm")

    means_no_cens.append(fitted_dist.mean)

    fitter2 = NetworkFitter(fracture_network, include_censoring=True)

    fitter2.fit('lognorm')

    fitted_dist2 = fitter2.get_fitted_distribution("lognorm")

    means_cens.append(fitted_dist2.mean)

    frac_censored.append(fracture_network.fraction_censored)

    # fracture_network.vtkplot()

    # plotter = pv.Plotter()
    # centers = pv.PolyData(xyz)
    # # plotter.add_mesh(centers, color='yellow')
    # plotter.add_mesh(circle, color='red')
    # plotter.add_mesh(lines, color='blue')
    # plotter.show()

sort = np.argsort(frac_censored)

plt.plot(np.array(frac_censored)[sort], np.array(means_no_cens)[sort], color='b')
plt.plot(np.array(frac_censored)[sort], np.array(means_cens)[sort], color='r')
plt.hlines(distr.mean(), xmin=np.min(frac_censored), xmax=np.max(frac_censored),
                   label='distribution mean', colors='k')
plt.show()