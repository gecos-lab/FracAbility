import pandas as pd
from reliability.Nonparametric import KaplanMeier
import matplotlib.pyplot as plt


data = pd.read_csv('Pontrelli_esf_test/output/csv/Fractures_1.csv', sep=';')

data = data.sort_values(by='length')

complete = data['length'][data['censored'] == 0]
censored = data['length'][data['censored'] == 1]

km = KaplanMeier(failures=complete, right_censored=censored, label='Failures + right censored', print_results=False)

km_estimate_censored = km.results['Kaplan-Meier Estimate'][km.results['Censoring code (censored=0)'] == 0]


plt.title('Kaplan-Meier estimates showing the\nimportance of including censored data')
plt.xlabel('Miles to failure')
plt.plot(censored, km_estimate_censored, 'xr')

plt.legend()
plt.show()
