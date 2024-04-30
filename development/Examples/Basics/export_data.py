"""
This example introduces the different ways that a FracAbility entity can be exported.
"""

import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)

from fracability import DATADIR  # import the path of the sample data
from fracability import Entities  # import the Entities class


# Import a fracture entity set
fracture_set1 = Entities.Fractures(shp=f'{DATADIR}/cava_pontrelli/Set_a.shp', set_n=1)


# Export such set as a shapefile

fracture_set1.save_shp(path='Basics')

# Export such set as a csv

fracture_set1.save_csv(path='Basics', sep=';')

