"""
Test akaike for comparing the 3 different estimation methods
"""

import scipy.stats as ss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


data = pd.read_csv('Fractures_test.csv', index_col=0)  # Read the data

data = data.sort_values(by='length')  # sort the data by length

lengths = data['length'].values  # Length value

sns.histplot(lengths)
plt.xlabel('Length [m]')
plt.show()
censored_value = data['censored'].values  # Censoring values: 0 is complete, 1 is censored

censored = data.loc[censored_value == 1, 'length']  # Extract only the censored values
uncensored = data.loc[censored_value == 0, 'length']  # Extract only the complete values


data_cens = ss.CensoredData(uncensored, right=censored)  # Create the scipy CensoredData instance


fit_all = ss.lognorm(*ss.lognorm.fit(lengths, floc=0))
fit_complete = ss.lognorm(*ss.lognorm.fit(uncensored, floc=0))
fit_survival = ss.lognorm(*ss.lognorm.fit(data_cens, floc=0))


max_like_all = np.sum(fit_all.logpdf(lengths))
max_like_complete = fit_complete.logpdf(uncensored).sum()
max_like_surv = fit_survival.logpdf(uncensored).sum()+fit_survival.logsf(censored).sum()

aic_all = (-2*max_like_all)+(2*len(fit_all.args))
aic_complete = (-2*max_like_complete)+(2*len(fit_complete.args))
aic_surv = (-2*max_like_surv)+(2*len(fit_survival.args))

print(aic_all, aic_complete, aic_surv)