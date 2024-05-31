from fracability.examples import data  # import the path of the sample data
from fracability import Entities, Statistics  # import the Entities class
from fracability.Plotters import matplot_tick_plot

pontrelli_data = data.Pontrelli()
data_dict = pontrelli_data.data_dict  # Get dict of paths for the data

# Create the fractures and boundary objects.
set_a = Entities.Fractures(shp=data_dict['Set_a.shp'], set_n=1)  # to add your data put the absolute path of the shp file

boundary = Entities.Boundary(shp=data_dict['Interpretation_boundary.shp'], group_n=1)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(set_a)

fracture_net.add_boundaries(boundary)

fracture_net.calculate_topology()

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




