from pyvista import PolyData
import time

from vtkmodules.vtkFiltersCore import vtkConnectivityFilter, vtkAppendPolyData

from fracability.Entities import BaseEntity
from fracability.utils.shp_operations import int_node
import numpy as np
from copy import deepcopy
from halo import Halo


def center_object(obj: BaseEntity, trans_center: np.array = None, return_center=False, inplace: bool = True ):

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


@Halo(text='Calculating intersections', spinner='line', placement='right')
def tidy_intersections(obj: BaseEntity, buffer=0.05, inplace: bool = True):

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
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = gdf
        return copy_obj


def calculate_seg_length(obj: BaseEntity, regions: [int] = None, inplace: bool = True):

    df = obj.entity_df.copy()

    lengths = df.length

    df.loc[:, 'length'] = lengths

    # connectivity = vtkConnectivityFilter()
    # connectivity.AddInputData(vtk_obj)
    # if regions is None:
    #     regions = set(vtk_obj['RegionId'])
    # lengths = []
    # for region in regions:
    #     connectivity.SetExtractionModeToSpecifiedRegions()
    #     connectivity.InitializeSpecifiedRegionList()
    #     connectivity.AddSpecifiedRegion(region)
    #     connectivity.Update()
    #     extr_obj = PolyData(connectivity.GetOutput())
    #     lengths.append(np.sum(extr_obj.compute_arc_length()['arc_length']))

    if inplace:
        obj.entity_df = df
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = df
        return copy_obj


