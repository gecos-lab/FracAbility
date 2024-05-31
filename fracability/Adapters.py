"""

Collection of methods used to pass from a geopandas dataframe to a polydata or from
polydata to networkx. Each method is fit so that it plots nodes, fractures, boundary or the fracture network

TODO:
    + Add a adapter abstract class in the AbstractClasses.
    + Use multiblock instead of appender for fracture network (or all?)?
    + Try and find a way to crate boundary vtk object directly from polygon and not from lines of polygon

"""

import geopandas
import networkx
import numpy as np
from pyvista import PolyData, lines_from_points, MultiBlock
from shapely.geometry import MultiLineString

from vtkmodules.vtkFiltersCore import vtkAppendPolyData

import networkx as nx
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter

from fracability.operations.Geometry import connect_dots
from fracability.utils.general_use import shp2vtk


#  =============== VTK representations ===============

def node_vtk_rep(input_df: geopandas.GeoDataFrame) -> PolyData:
    points_vtk = shp2vtk(input_df)
    # points = np.array([point.coords for point in input_df.geometry]).reshape(-1, 3)
    # types = input_df['type'].values
    # node_types = input_df['n_type'].values
    #
    # points_vtk = PolyData(points)
    # points_vtk['type'] = types
    # points_vtk['n_type'] = node_types

    return points_vtk


def frac_vtk_rep(input_df: geopandas.GeoDataFrame) -> PolyData:

    conn_obj = shp2vtk(input_df)
    # appender = vtkAppendPolyData()
    #
    # for index, geom, set_n in zip(input_df.index, input_df['geometry'],
    #                               input_df['f_set']):  # For each geometry in the df
    #
    #     x, y = geom.coords.xy  # get xy as an array
    #     z = np.zeros_like(x)  # create a zeros z array with the same dim of the x (or y)
    #
    #     points = np.stack((x, y, z), axis=1)  # Stack the coordinates to a [n,3] shaped array
    #     # offset = np.round(points[0][0])
    #     if len(points) != 0:  # Avoid empty geometries
    #         pv_obj = lines_from_points(points)  # Create the corresponding vtk line with the given points
    #         pv_obj.cell_data['type'] = ['fracture'] * pv_obj.GetNumberOfCells()
    #         pv_obj.point_data['type'] = ['fracture'] * pv_obj.GetNumberOfPoints()
    #
    #         pv_obj.cell_data['f_set'] = [set_n] * pv_obj.GetNumberOfCells()
    #         pv_obj.point_data['f_set'] = [set_n] * pv_obj.GetNumberOfPoints()
    #
    #         pv_obj.cell_data['RegionId'] = [index] * pv_obj.GetNumberOfCells()
    #         pv_obj.point_data['RegionId'] = [index] * pv_obj.GetNumberOfPoints()
    #
    #         if 'length' in input_df.columns:
    #             pv_obj.cell_data['length'] = input_df.loc[index, 'length']
    #
    #     appender.AddInputData(pv_obj)  # Add the new object
    #
    # geometry_filter = vtkGeometryFilter()
    # geometry_filter.SetInputConnection(appender.GetOutputPort())
    # geometry_filter.Update()
    #
    # output_obj = PolyData(geometry_filter.GetOutput())
    # conn_obj = connect_dots(output_obj)

    return conn_obj


def bound_vtk_rep(input_df: geopandas.GeoDataFrame) -> PolyData:

    conn_obj = shp2vtk(input_df)
    # appender = vtkAppendPolyData()
    #
    # for index, geom, b_group in zip(input_df.index,
    #                                 input_df['geometry'],
    #                                 input_df['b_group']):  # For each geometry in the df
    #
    #     x, y = geom.coords.xy  # get xy as an array
    #     z = np.zeros_like(x)  # create a zeros z array with the same dim of the x (or y)
    #
    #     points = np.stack((x, y, z), axis=1)  # Stack the coordinates to a [n,3] shaped array
    #     # offset = np.round(points[0][0])
    #     pv_obj = lines_from_points(points)  # Create the corresponding vtk line with the given points
    #     pv_obj.cell_data['type'] = ['boundary'] * pv_obj.GetNumberOfCells()
    #     pv_obj.point_data['type'] = ['boundary'] * pv_obj.GetNumberOfPoints()
    #
    #     pv_obj.cell_data['b_group'] = [b_group] * pv_obj.GetNumberOfCells()
    #     pv_obj.point_data['b_group'] = [b_group] * pv_obj.GetNumberOfPoints()
    #
    #     pv_obj.cell_data['RegionId'] = [index] * pv_obj.GetNumberOfCells()
    #     pv_obj.point_data['RegionId'] = [index] * pv_obj.GetNumberOfPoints()
    #
    #
    #     # line.plot()
    #
    #     appender.AddInputData(pv_obj)  # Add the new object
    #
    # geometry_filter = vtkGeometryFilter()
    # geometry_filter.SetInputConnection(appender.GetOutputPort())
    # geometry_filter.Update()
    #
    # output_obj = PolyData(geometry_filter.GetOutput())
    # conn_obj = connect_dots(output_obj)

    return conn_obj


def fracture_network_vtk_rep(input_df: geopandas.GeoDataFrame, include_nodes=True) -> PolyData:

    fractures_df = input_df.loc[input_df['type'] == 'fracture']
    boundaries_df = input_df.loc[input_df['type'] == 'boundary']

    appender = vtkAppendPolyData()

    if include_nodes:
        nodes_df = input_df.loc[input_df['type'] == 'node']
        if not nodes_df.empty:
            nodes_vtk = node_vtk_rep(nodes_df)
            appender.AddInputData(nodes_vtk)

    if not fractures_df.empty:
        fractures_vtk = frac_vtk_rep(fractures_df)
        appender.AddInputData(fractures_vtk)
    if not boundaries_df.empty:
        boundaries_vtk = bound_vtk_rep(boundaries_df)
        appender.AddInputData(boundaries_vtk)

    appender.Update()

    geometry_filter = vtkGeometryFilter()
    geometry_filter.SetInputConnection(appender.GetOutputPort())
    geometry_filter.Update()

    output_obj = PolyData(geometry_filter.GetOutput())
    conn_obj = connect_dots(output_obj)

    return conn_obj


#  =============== Networkx representations ===============


def networkx_rep(input_object: PolyData) -> networkx.Graph():

    network = input_object
    lines = network.lines  # Get the connectivity list of the object

    lines = np.delete(lines,
                      np.arange(0, lines.size, 3)).reshape(-1, 2)  # remove padding eg. [2 id1 id2 2 id3 id4 ...] -> remove the 2

    network = nx.Graph()  # Create a networkx graph instance

    network.add_edges_from(lines)  # Add the edges

    output_obj = network
    return output_obj

