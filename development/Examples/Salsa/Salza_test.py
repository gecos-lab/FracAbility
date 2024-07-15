from fracability.examples import data  # import the path of the sample data
from fracability import Entities, Statistics  # import the Entities class

salza_data = data.Salza()
data_dict = salza_data.data_dict  # Get dict of paths for the data

# Create the fractures and boundary objects.
fracture_set1 = Entities.Fractures(shp=data_dict['Set_1.shp'], set_n=1)  # to add your data put the absolute path of the shp file
fracture_set2 = Entities.Fractures(shp=data_dict['Set_2.shp'], set_n=2)  # to add your data put the absolute path of the shp file

boundary = Entities.Boundary(shp=data_dict['Interpretation_boundary.shp'], group_n=1)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_set1)
fracture_net.add_fractures(fracture_set2)

fracture_net.add_boundaries(boundary)
fracture_net.calculate_topology()

fracture_net.save_shp('Salza')
fracture_net.save_csv('Salza')

# fracture_net.activate_fractures([1])
# fitter = Statistics.NetworkFitter(fracture_net)
#
# fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('powerlaw')
# fitter.fit('weibull_min')
#
# fitter.fit_result_to_clipboard()
# fitter.plot_PIT(bw=True)
# fitter.plot_summary(position=[1], sort_by='Mean_rank')
#
# fracture_net.activate_fractures([2])
# fitter = Statistics.NetworkFitter(fracture_net)
#
# fitter.fit('lognorm')
# fitter.fit('expon')
# fitter.fit('norm')
# fitter.fit('gamma')
# fitter.fit('powerlaw')
# fitter.fit('weibull_min')
#
# # fitter.fit_result_to_clipboard()
# fitter.plot_PIT(bw=True, n_ticks=11)
# fitter.plot_summary(position=[1], sort_by='Mean_rank')
# # fitter.tick_plot(n_ticks=5)
