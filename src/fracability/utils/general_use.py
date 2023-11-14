import scooby
import pyperclip


def report():
    core = ['fracability', 'pyvista', 'vtk', 'numpy', 'geopandas', 'shapely']
    text = scooby.Report(core=core, ncol=3, text_width=80, sort=True, additional=None, optional=None)
    print(text)
    pyperclip.copy(str(text))
    print('Report copied to clipboard')



