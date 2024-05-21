
import pyvista as pv
import geopandas as gpd
import pandas as pd
import numpy as np
from vtkmodules.vtkFiltersCore import vtkCleanPolyData
from shapely.geometry import LineString, Point
from fracability import Entities


def vtk2shp(vtk_file, nodes=False):
    dataframe = gpd.GeoDataFrame.from_dict(dict(vtk_file.cell_data))
    for idx, cell in enumerate(vtk_file.cell):
        if nodes:
            dataframe.loc[idx, 'geometry'] = Point(cell.points)
        else:
            dataframe.loc[idx, 'geometry'] = LineString(cell.points)

    return dataframe


vtk_file = pv.read('fractures.vtk')

nodes = vtk_file.cast_to_poly_points()
nodes = nodes.point_data_to_cell_data()

print(nodes.cell_data)

print(vtk2shp(nodes, 'nodes'))