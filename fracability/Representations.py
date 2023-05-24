import geopandas
import pandas
import numpy as np
from pyvista import PolyData, lines_from_points
from shapely import LineString
from vtkmodules.vtkFiltersCore import vtkAppendPolyData, vtkConnectivityFilter, vtkCleanPolyData
from abc import ABC, abstractmethod
import networkx as nx

class Representation(ABC):
    """
    Abstract class used to represent in different ways the geopandas dataframe
    """
    def __init__(self):
        self.input_object = None
        self.output_obj = None

    @abstractmethod
    def set_input(self, obj):
        """
        Set the input of the Representation.
        :param obj: The input depends on the concrete class (for example VTKRepr accepts a gdf dataframe)

        :return:
        """

    @abstractmethod
    def process_pipeline(self):
        """
        Process the input data depending on the different representations
        (e.g. VTK pipeline will be different from the NetworkX pipeline).
        """
        pass

    def get_repr(self):
        """
        Get the desired representation output
        :return: The output depends on the concrete class (for example VTKRepr returns a VTK object)
        """
        return self.output_obj


class VTKRepr(Representation):
    """
    Get the geopandas dataframe representation as a vtk object. Each line of the
    dataframe is scanned and the points extracted to form a polyline (with lines_from_points).

    To each cell the attribute "type" is assigned
    (should be 'node', 'fracture', 'boundary')
    """
    def set_input(self, obj: geopandas.GeoDataFrame):
        self.input_object = obj
        self.process_pipeline()

    def process_pipeline(self):
        appender = vtkAppendPolyData()
        p = 100000  # Scaling factor needed for the vtk functions to work properly

        for line, l_type in zip(self.input_object['geometry'], self.input_object['type']):  # For each geometry in the df

            x, y = line.coords.xy  # get xy as an array
            z = np.zeros_like(x)  # create a zeros z array with the same dim of the x (or y)

            points = np.stack((x, y, z), axis=1)  # Stack the coordinates to a [n,3] shaped array
            points *= p  # Multiply the coordinates with the factor
            # offset = np.round(points[0][0])
            pv_line = lines_from_points(points)  # Create the corresponding vtk line with the given points
            pv_line.cell_data['type'] = [l_type] * pv_line.GetNumberOfCells()
            # line.plot()
            appender.AddInputData(pv_line)  # Add the new object

        # Set the RegionId of each line
        connectivity = vtkConnectivityFilter()

        connectivity.AddInputConnection(appender.GetOutputPort())
        connectivity.SetExtractionModeToAllRegions()
        connectivity.ColorRegionsOn()

        # Fuse overlapping points
        clean = vtkCleanPolyData()
        clean.AddInputConnection(connectivity.GetOutputPort())
        clean.ToleranceIsAbsoluteOn()
        clean.SetTolerance(1)
        clean.ConvertLinesToPointsOff()
        clean.ConvertPolysToLinesOff()
        clean.ConvertStripsToPolysOff()
        clean.Update()

        self.output_obj = PolyData(clean.GetOutput())
        self.output_obj.points /= p


class NetworkxRepr(Representation):
    """
    Class used to generate a networkx representation of the fracture network (VTK)
    """
    def set_input(self, obj: PolyData):
        self.input_object = obj
        self.process_pipeline()

    def process_pipeline(self):

        network = self.input_object
        lines = network.lines  # Get the connectivity list of the object

        lines = np.delete(lines,
                          np.arange(0, lines.size, 3))  # remove padding eg. [2 id1 id2 2 id3 id4 ...] -> remove the 2

        network = nx.Graph()  # Create a networkx graph instance

        network.add_edges_from(lines.reshape(-1, 2))  # Add the edges

        self.output_obj = network

    def get_vtk_repr(self) -> PolyData:
        return self.input_object
    
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



