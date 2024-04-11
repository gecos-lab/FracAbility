"""
Calculate and plot PDF and SF of the exponential distribution
"""


import numpy as np
from numpy import exp as e
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as ss
sns.set_theme()



# exp_dist = ss.exp()
x = np.linspace(0, 40, 1000)
# pdf = l*e(-l*x)
pdf = ss.pareto.pdf(x, b=1)
# cdf = 1-e(-l*x)
# sf = 1-cdf
sf = ss.pareto.sf(x, b=1)
sns.lineplot(x=x, y=pdf)
plt.xlabel('Length [m]')
plt.ylabel('Probability density')
plt.title('Exponential distribution PDF (F)')
plt.show()

sns.lineplot(x=x, y=sf)
plt.xlabel('Length [m]')
plt.ylabel('Survival probability')
plt.title('Exponential distribution SF (S)')
plt.show()

