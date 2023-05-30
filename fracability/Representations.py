import geopandas
import networkx
import pandas
import numpy as np
from pyvista import PolyData, lines_from_points
from shapely.geometry import LineString, Point
from vtkmodules.vtkFiltersCore import vtkAppendPolyData, vtkConnectivityFilter, vtkCleanPolyData, vtkAppendArcLength
from abc import ABC, abstractmethod
import networkx as nx


def vtk_rep(input_df: geopandas.GeoDataFrame) -> PolyData:
    appender = vtkAppendPolyData()

    for geom, l_type in zip(input_df['geometry'], input_df['type']):  # For each geometry in the df

        x, y = geom.coords.xy  # get xy as an array
        z = np.zeros_like(x)  # create a zeros z array with the same dim of the x (or y)

        points = np.stack((x, y, z), axis=1)  # Stack the coordinates to a [n,3] shaped array
        # offset = np.round(points[0][0])
        pv_obj = lines_from_points(points)  # Create the corresponding vtk line with the given points
        pv_obj.cell_data['type'] = [l_type] * pv_obj.GetNumberOfCells()
        pv_obj.point_data['type'] = [l_type] * pv_obj.GetNumberOfPoints()
        # line.plot()

        appender.AddInputData(pv_obj)  # Add the new object

    # Set the RegionId of each line
    connectivity = vtkConnectivityFilter()

    connectivity.AddInputConnection(appender.GetOutputPort())
    connectivity.SetExtractionModeToAllRegions()
    connectivity.ColorRegionsOn()
    connectivity.Update()

    output_obj = PolyData(connectivity.GetOutput())

    return output_obj


def networkx_rep(input_object: PolyData) -> networkx.Graph:

    network = input_object
    lines = network.lines  # Get the connectivity list of the object

    lines = np.delete(lines,
                      np.arange(0, lines.size, 3))  # remove padding eg. [2 id1 id2 2 id3 id4 ...] -> remove the 2

    test_types = np.array([{'type': t} for t in network['type']])
    edges = np.c_[lines.reshape(-1, 2), test_types]

    network = nx.Graph()  # Create a networkx graph instance

    network.add_edges_from(edges)  # Add the edges

    output_obj = network
    return output_obj





    # def plot(self):
    #     """
    #     Method used to plot the networkx graph
    #     :return:
    #     """
    #
    #     nx.draw(self.output_obj)
    #     plt.show()


# class GPDRepr(Representation):
#     """
#     Get the Geopandas dataframe representation of a vtk object
#     """
#     def set_input(self,repr_obj: BaseEntity):
#
#     def get_output(self, repr_obj: PolyData) -> geopandas.GeoDataFrame:
#
#         gdf = geopandas.GeoDataFrame(pandas.DataFrame(
#             {'type': [], 'U-nodes': [], 'geometry': []}))
#
#         ids = set(repr_obj['RegionId'])
#         for i, idx in enumerate(ids):
#             extr = repr_obj.extract_points(repr_obj['RegionId'] == idx)
#             points = extr.points
#             line = LineString(points)
#             extr_type = list(set(extr['type']))[0]



