from abc import ABC, abstractmethod

import geopandas
import matplotlib.pyplot as plt

from pyvista import PolyData
import time

from vtkmodules.vtkFiltersCore import vtkConnectivityFilter, vtkCleanPolyData, vtkAppendPolyData

from fracability.Entities import Fractures, BaseEntity, FractureNetwork
from fracability.utils.shp_operations import int_node
import numpy as np
from copy import deepcopy


def center_object(obj: BaseEntity, trans_center: np.array = None, return_center=False, inplace: bool = True ):
    """
    Center the network. If the translation point is not
    given then the centroid of the network will coincide with the world origin.
    :param trans_center: Point to translate to
    :param return_center: Flag to enable the return of the translation center
    :return:
    """

    df = obj.entity_df.copy()

    if trans_center is None:
        trans_center = np.array(df.dissolve().centroid[0].coords).flatten()

    df['geometry'] = df.translate(-trans_center[0], -trans_center[1])
    if return_center:
        return trans_center

    if inplace:
        obj.entity_df = df
        obj.process_df()
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = df
        return copy_obj


def tidy_intersections(obj: BaseEntity, buffer=0.05, inplace: bool = True):
    """
        Tidy intersections of the fracture network (without the boundary).
        For this function to properly work it is advised also to center the dataframe t
        o avoid rounding errors. A buffer is applied to be sure that lines touch.
        :param obj: Input object entity object
        :param buffer: Buffer value applied to the network
    """

    gdf = obj.entity_df.copy()
    df_buffer = gdf.buffer(buffer)
    
    start = time.time()
    for idx_line1, line in gdf.iterrows():
        if line['type'] == 'boundary':
            continue
        line1 = line['geometry']

        idx_list = df_buffer.index[df_buffer.intersects(line1) == True]  # Subset the intersecting lines
        idx_list = idx_list[idx_list != idx_line1]  # Exclude the reference line index to avoid self intersection

        intersections = gdf.loc[idx_list]
        for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:
            new_geom = int_node(line1, line2, [idx_line1, idx_line2])  # Calculate and add the intersection node.

            for key, value in new_geom.items():
                gdf.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry

            line1 = gdf.loc[
                idx_line1, 'geometry']  # Use as the reference line (in the int_node function) the new geometry.

    if inplace:
        obj.entity_df = gdf
        obj.process_df()
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = gdf
        return copy_obj


def connect_dots(obj: BaseEntity, inplace: bool = True):

    vtk_obj = obj.vtk_object
    p = 100000  # Scaling factor needed for the vtk function to work properly
    vtk_obj.points *= p
    clean = vtkCleanPolyData()
    clean.AddInputData(vtk_obj)
    clean.ToleranceIsAbsoluteOn()
    clean.ConvertLinesToPointsOff()
    clean.ConvertPolysToLinesOff()
    clean.ConvertStripsToPolysOff()
    clean.Update()

    output_obj = PolyData(clean.GetOutput())
    output_obj.points /= p

    if inplace:
        obj.vtk_object = output_obj
    else:
        copy_obj = deepcopy(obj)
        copy_obj.vtk_object = output_obj
        return copy_obj


def calculate_seg_length(obj: BaseEntity, regions: [int] = None, inplace: bool = True):
    vtk_obj = obj.vtk_object
    connectivity = vtkConnectivityFilter()
    connectivity.AddInputData(vtk_obj)
    if regions is None:
        regions = set(vtk_obj['RegionId'])
    appender = vtkAppendPolyData()
    for region in regions:
        connectivity.SetExtractionModeToSpecifiedRegions()
        connectivity.InitializeSpecifiedRegionList()
        connectivity.AddSpecifiedRegion(region)
        connectivity.Update()
        extr_obj = PolyData(connectivity.GetOutput())
        extr_obj.field_data['segment_length'] = np.sum(extr_obj.compute_arc_length()['arc_length'])
        appender.AddInputData(extr_obj)
    appender.Update()
    if inplace:
        obj.vtk_object = PolyData(appender.GetOutput())
    else:
        copy_obj = deepcopy(obj)
        copy_obj.vtk_object = PolyData(appender.GetOutput())
        return copy_obj

