import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import pandas as pd
import seaborn as sns

l = 1
x = np.linspace(0,1, num=100000)
number_of_samples = 5000
samples = np.random.exponential(l, number_of_samples)
samples.sort()


Z = 1-np.exp(-l*samples)
Z.sort()
z_list = np.linspace(0, 1, num=1000)

G = np.zeros_like(Z)

for i, z in enumerate(Z):
    if z < Z[0]:
        G[i] = 0
    elif z > Z[-1]:
        G[i] = 1
    else:
        list_products = np.array([])
        j_index = np.where(Z <= z)[0]
        for j in j_index:
            term = ((number_of_samples-j)/(number_of_samples-j+1))
            list_products = np.append(list_products, term)
        G[i] = 1-np.prod(list_products)



# print(G)

ecdf = ss.ecdf(Z).cdf
ecdfG = ss.ecdf(G).cdf
plt.plot(ecdf.quantiles, ecdf.probabilities,label='ecdf')
plt.plot(z_list, ss.uniform.cdf(z_list), label='uniform')
plt.plot(z_list, G, label='KM')
plt.legend()
plt.show()
