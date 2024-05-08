"""
This example introduces the different ways that a fracture network can be imported. We then visualize such
network using vtk and matplotlib
"""
import os.path

from fracability.examples import data  # import the path of the sample data
from fracability import Entities  # import the Entities class

pontrelli_data = data.Pontrelli()

# Display available file names for the Pontrelli dataset

print(pontrelli_data.available_data)


# Build the complete fracture network object

data_dict = pontrelli_data.data_dict  # Get dict of paths for the data

set_a = Entities.Fractures(shp=data_dict['Set_a.shp'], set_n=1)
set_b = Entities.Fractures(shp=data_dict['Set_b.shp'], set_n=2)
set_c = Entities.Fractures(shp=data_dict['Set_c.shp'], set_n=3)

boundary = Entities.Boundary(shp=data_dict['Interpretation_boundary.shp'], group_n=1)


set_a.vtk_plot(linewidth=0.1)

# fracture_net = Entities.FractureNetwork()
#
# fracture_net.add_fractures(set_a)
# fracture_net.add_fractures(set_b)
# fracture_net.add_fractures(set_c)
# fracture_net.add_boundaries(boundary)
#
# # Plot the fracture network using VTK
#
# fracture_net.vtk_plot()
#
# # Plot the fracture network using matplot
# fracture_net.mat_plot()





