"""
Test used to see how lognorm works on scipy
"""

import numpy as np
import scipy.stats as ss
import seaborn as sns
import matplotlib.pyplot as plt


mu = 2
sigma = 2

var_normal = np.log((sigma**2/(mu**2))+1)

m_normal = np.log(mu)-var_normal/2

l = ss.lognorm(s=np.sqrt(var_normal), loc=0, scale=np.exp(m_normal))

print(l.mean())

print(m_normal)

random = l.rvs(size=1000)

sns.histplot(random)
plt.show()


