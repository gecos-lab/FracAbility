from fracability.examples import data
from fracability import Entities, Statistics
import numpy as np
import matplotlib.pyplot as plt
from reliability.Nonparametric import KaplanMeier

pontrelli = data.Pontrelli()

data_dict = pontrelli.data_dict  # Get dict of paths for the data

set_a_path = data_dict['Set_a.shp']
boundary_path = data_dict['Interpretation_boundary.shp']


set_a = Entities.Fractures(shp=set_a_path, set_n=1)

boundary = Entities.Boundary(shp=boundary_path)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(set_a)
fracture_net.add_boundaries(boundary)

fracture_net.calculate_topology()

# fracture_net.save_csv('Pontrelli_esf_test')

fitter = Statistics.NetworkFitter(fracture_net)

esf = fitter.network_data.esf
lengths = fitter.network_data.lengths

# lengths = np.insert(lengths, 0, 0)

index = np.where(fracture_net.fractures.entity_df.sort_values(by='length')['censored'] == 1)[0]

plt.title('Kaplan-Meier estimator')
plt.step(lengths, esf, label='Estimated survival function', where='post')
plt.plot(fitter.network_data.censored_lengths, esf[index], 'xr', label='Censored values', markersize=7)
# KaplanMeier(failures=fitter.network_data.non_censored_lengths, right_censored=fitter.network_data.censored_lengths,
#             plot_type='SF', print_results=False, label='Reliability')

plt.xlabel('Length [m]')
plt.ylabel('Fraction surviving')
plt.legend()
plt.show()