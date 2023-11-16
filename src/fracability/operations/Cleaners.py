from copy import deepcopy

from pyvista import PolyData, Plotter
from vtkmodules.vtkFiltersCore import vtkCleanPolyData

# from fracability.Entities import BaseEntity


# def clean_dup_points(obj: BaseEntity):
#     df = obj.entity_df
#     df['geometry'] = df['geometry'].simplify(0)


# def connect_dots(obj: BaseEntity, inplace: bool = True):
#
#     vtk_obj = obj.vtk_object
#     p = 100000  # Scaling factor needed for the vtk function to work properly
#     vtk_obj.points *= p
#     clean = vtkCleanPolyData()
#     clean.AddInputData(vtk_obj)
#     clean.ToleranceIsAbsoluteOn()
#     clean.ConvertLinesToPointsOff()
#     clean.ConvertPolysToLinesOff()
#     clean.ConvertStripsToPolysOff()
#     clean.Update()
#
#     output_obj = PolyData(clean.GetOutput())
#     output_obj.points /= p
#
#     if inplace:
#         obj.vtk_object = output_obj
#     else:
#         copy_obj = deepcopy(obj)
#         copy_obj.vtk_object = output_obj
#         return copy_obj
def connect_dots(vtk_obj: PolyData) -> PolyData:

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

    return output_obj

