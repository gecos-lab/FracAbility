import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import Entities
from fracability import DATADIR



# Pontrelli
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1, check_geometry=False)
fracture_set2 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_b.shp', set_n=2, check_geometry=False)
fracture_set3 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_c.shp', set_n=3, check_geometry=False)
boundary = Entities.Boundary(shp=f'{DATADIR}/cava_pontrelli/Interpretation-boundary.shp', group_n=1)



fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)
fracture_net.add_fractures(fracture_set3)

fracture_net.add_boundaries(boundary)

# print('ciao')
fracture_net.calculate_topology()
vtkbackbone = fracture_net.calculate_backbone()

backbone = Entities.Fractures(set_n=4)
backbone.vtk_object = vtkbackbone
backbone.crs = fracture_set1.crs
fracture_net.add_fractures(backbone)

fracture_net.deactivate_fractures([1, 2, 3])

fracture_net.calculate_topology()
fracture_net.ternary_plot()


backbone.save_shp('output_Pontrelli/backbone')




