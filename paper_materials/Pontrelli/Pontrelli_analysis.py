'''
Script used to analyse the Pontrelli dataset.
'''

from fracability import Entities, Statistics  # import the Entities class

data_path = 'Pontrelli_in/Set_a.shp'
boundary_path = 'Pontrelli_in/Interpretation_boundary.shp'

# Create the fractures and boundary objects.
set_a = Entities.Fractures(shp=data_path, set_n=1)  # to add your data put the absolute path of the shp file

boundary = Entities.Boundary(shp=boundary_path, group_n=1)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(set_a)

fracture_net.add_boundaries(boundary)

fracture_net.calculate_topology()

fracture_net.vtk_plot(notebook=False)

fracture_net.fractures.save_csv('Pontrelli_out')


fitter = Statistics.NetworkFitter(fracture_net)

fitter.fit('lognorm')
fitter.fit('expon')
fitter.fit('norm')
fitter.fit('gamma')
fitter.fit('powerlaw')
fitter.fit('weibull_min')


fitter.plot_PIT(bw=True)
fitter.plot_summary(position=[1], sort_by='Mean_rank')
# fitter.fit_result_to_clipboard()
# Plotters.matplot_stats_ranks(fitter)




