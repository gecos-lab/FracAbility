import pandas as pd
from fracability import Entities, Statistics
import numpy as np
from tracemalloc import Statistic

n_data = 1000
random_data = np.random.randn(n_data)
random_censoring = np.random.binomial(n=1, p=0.2, size=n_data)

data = pd.DataFrame()
data['length'] = random_data
data['censored'] = random_censoring

fitter = Statistics.NetworkFitter(data)
fitter.fit('norm')
fitter.fit('expon')
fitter.fit('gengamma')

fitter.plot_PIT(bw=True)
