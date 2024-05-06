"""
This example introduces the different ways that a fracture network can be imported. We then visualize such
network using vtk and matplotlib
"""
import os.path

from fracability import pontrelli_dir  # import the path of the sample data
from fracability import Entities  # import the Entities class

# Import a fracture entity set
fracture_set1 = Entities.Fractures(shp=os.path.join(pontrelli_dir, 'set_a.shp'), set_n=1)

# Plot such fracture entity using vtk

fracture_set1.vtk_plot()

# Plot such fracture entity using matplotlib

fracture_set1.mat_plot()




