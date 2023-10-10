
from fracability import Entities
from fracability.Plotters import matplot_stats_summary
from fracability.operations.Geometry import tidy_intersections
from fracability.operations.Statistics import NetworkFitter
from fracability.operations.Topology import nodes_conn

from fracability.examples import example_fracture_network


shp_path, _ = example_fracture_network.fracture_net()


cava_set1 = '/home/gabriele/STORAGE/projects/FracAbility/fracability/datasets/cava_pontrelli/FN_set_1.shp'
cava_bounary = '/home/gabriele/STORAGE/projects/FracAbility/fracability/datasets/cava_pontrelli/Interpretation-boundary.shp'

# set_1 = shp_path['set_1']
# set_2 = shp_path['set_2']


fractures_1 = Entities.Fractures(shp=cava_set1, set_n=1)
# fractures_2 = Entities.Fractures(shp=set_2, set_n=2)

boundaries = Entities.Boundary(shp=cava_bounary)

fracture_net = Entities.FractureNetwork()


fracture_net.add_boundaries(boundaries)

fracture_net.add_fractures(fractures_1)

tidy_intersections(fracture_net)

nodes_conn(fracture_net)

# fracture_net.vtkplot()
#
fitter = NetworkFitter(fracture_net, include_censoring=False)

fitter.fit('lognorm')

matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))

fitter2 = NetworkFitter(fracture_net, include_censoring=True)

fitter2.fit('lognorm')

print(fitter2.get_fitted_parameters('lognorm'))

matplot_stats_summary(fitter2.get_fitted_distribution('lognorm'))