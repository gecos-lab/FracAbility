"""
This example introduces the different ways that a fracture network can be imported. We then visualize such
network using vtk and matplotlib
"""

import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import DATADIR  # import the path of the sample data
from fracability import Entities  # import the Entities class


# Import a fracture entity set
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1)

# Plot such fracture entity using vtk

fracture_set1.vtk_plot()

# Plot such fracture entity using matplotlib

fracture_set1.mat_plot()




