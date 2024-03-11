import numpy as np
import matplotlib.pyplot as plt

start = 1
stop = 345000
n_points = 500


linspace = np.linspace(start, stop, n_points)
logspace = np.logspace(start, stop, n_points)
geomspace = np.geomspace(start, stop, n_points)


plt.plot(linspace, np.repeat(1, n_points), 'ro', label='linear')
# plt.plot(np.log10(logspace), np.repeat(2, n_points), 'go', label='log')
plt.plot(geomspace, np.repeat(3, n_points), 'bo', label='geom')
plt.legend()
plt.show()

