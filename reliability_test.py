import reliability as rel
from reliability.Other_functions import histogram
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('/home/gabriele/STORAGE/projects/Ntwrk/rerobe/Fracture_network.shp_length_dist.csv')


uncens_data = data.loc[data['U-nodes'] == 0, 'length'].values
cens_data = data.loc[data['U-nodes'] == 1, 'length'].values

test_data = data['length'].values


fitter = rel.Fitters.Fit_Everything(failures=test_data,
                                  show_probability_plot=False,
                                  print_results=False,
                                  show_histogram_plot=False,
                                  downsample_scatterplot=False,
                                  show_PP_plot=False,
                                  show_best_distribution_probability_plot=False)


best = fitter.best_distribution
print(fitter.results)

test = rel.Reliability_testing.KStest(best, test_data)
plt.show()
