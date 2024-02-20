import pyvista as pv
from vtk import vtkCommand
import time


def callback(a, b):

    new_center = list(plotter.camera.focal_point)
    distance = plotter.camera.distance
    new_center[2] = 0
    # time.sleep(0.1)
    plane = pv.Plane(center=new_center, direction=(0, 0, 1), i_size=distance/2, j_size=distance/2,i_resolution=int(100/distance), j_resolution=int(100/distance))
    plotter.add_mesh(plane, name='plane', style='wireframe')
    plotter.camera.focal_point = plane.center


plotter = pv.Plotter()

plotter.iren.add_observer(vtkCommand.EndInteractionEvent, callback)

new_center = list(plotter.camera.focal_point)
distance = plotter.camera.distance
new_center[2] = 0
plane = pv.Plane(center=new_center, direction=(0, 0, 1), i_size=distance/2, j_size=distance/2, i_resolution=int(100/distance), j_resolution=int(100/distance))
plotter.add_mesh(plane, name='plane', style='wireframe')
plotter.background_color = 'gray'
plotter.add_camera_orientation_widget()

plotter.show()