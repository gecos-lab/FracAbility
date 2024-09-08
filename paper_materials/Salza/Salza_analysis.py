'''
Script used to analyse the Colle Salza dataset
'''

from fracability import Entities, Statistics  # import the Entities class

data_path_1 = 'Salza_in/Set_1.shp'
data_path_2 = 'Salza_in/Set_2.shp'

boundary_path = 'Salza_in/Interpretation_boundary.shp'

# Create the fractures and boundary objects.
fracture_set1 = Entities.Fractures(shp=data_path_1, set_n=1)  # to add your data put the absolute path of the shp file
fracture_set2 = Entities.Fractures(shp=data_path_2, set_n=2)  # to add your data put the absolute path of the shp file

boundary = Entities.Boundary(shp=boundary_path, group_n=1)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)

fracture_net.add_boundaries(boundary)
fracture_net.calculate_topology()
fracture_net.vtk_plot(notebook=False)
fracture_net.fractures.save_csv('Salza_out')

fracture_net.activate_fractures([1])
fitter = Statistics.NetworkFitter(fracture_net)

fitter.fit('lognorm')
fitter.fit('expon')
fitter.fit('norm')
fitter.fit('gamma')
fitter.fit('powerlaw')
fitter.fit('weibull_min')

# fitter.fit_result_to_clipboard()
fitter.plot_PIT(bw=True,n_ticks=6)
fitter.plot_summary(position=[1], sort_by='Mean_rank')

fracture_net.activate_fractures([2])
fitter = Statistics.NetworkFitter(fracture_net)

fitter.fit('lognorm')
fitter.fit('expon')
fitter.fit('norm')
fitter.fit('gamma')
fitter.fit('powerlaw')
fitter.fit('weibull_min')

# fitter.fit_result_to_clipboard()
fitter.plot_PIT(bw=True, n_ticks=6)
fitter.plot_summary(position=[1], sort_by='Mean_rank')

