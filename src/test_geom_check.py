from fracability import Entities
from fracability.operations import Statistics
from fracability import Plotters
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import shapely as shp


fracture_set1 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_bkp/Fracture_network_H.shp', set_n=1)

fracture_set2 = Entities.Fractures(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_bkp/Fracture_network.shp', set_n=2)

boundary = Entities.Boundary(shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_bkp/Interpretation_boundary.shp', group_n=1)

# fracture_set2.check_geometries()

frac_net = Entities.FractureNetwork()

frac_net.add_fractures(fracture_set1)
frac_net.add_fractures(fracture_set2)
frac_net.add_boundaries(boundary)

# print(frac_net.fracture_network_to_components_df())
# test_b = boundary.entity_df.loc[0, 'geometry']
# test_f = fracture_set2.entity_df.loc[4, 'geometry']
# #
# mask = np.ones(frac_net.fracture_network_to_components_df().geometry.size, dtype=bool)
# mask[-1] = False
# #
# intersections = frac_net.fracture_network_to_components_df().intersects(test_b)[mask]
# touching = frac_net.fracture_network_to_components_df().touches(test_b)[mask]
# # crossings = frac_net.fracture_network_to_components_df().crosses(test_b)[mask]
#
# xor = intersections != touching
#
# # xor2 = xor != crossings
# #
# print(frac_net.fracture_network_to_components_df()[mask][xor])


# # Plot results to visualize intersections
#
# test2 = np.array(test_f.coords)
# test1 = test_b
#
# # p = gpd.GeoSeries(test1)
# # p.plot()
# #
# # # plt.plot(test1[:, 0], test1[:, 1], 'r')
# # plt.plot(test2[:, 0], test2[:, 1], 'r-o')
# # plt.show()
# # # print(test_f)
# #
# # print(test1.intersects(test_f))
# # print(test1.touches(test_f))
#
# frac_net.check_network(save_shp='/home/gabriele/STORAGE/projects/Ivan/Fracture_interpretation_bkp')
frac_net.check_network()

# # print(frac_net.fracture_network_to_components_df())