import reliability as rel
from reliability.Other_functions import histogram
from reliability.Utils import generate_X_array
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('/home/gabriele/STORAGE/projects/Ntwrk/rerobe/Fracture_network.shp_length_dist.csv')


uncens_data = data.loc[data['U-nodes'] == 0, 'length'].values
cens_data = data.loc[data['U-nodes'] == 1, 'length'].values

test_data = data['length'].values


fitter = rel.Fitters.Fit_Everything(failures=uncens_data, right_censored=cens_data)

print(fitter.best_distribution_name)
