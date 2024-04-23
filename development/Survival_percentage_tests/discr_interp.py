import numpy as np
import matplotlib.pyplot as plt

N = 10
xmin, xmax = 0., 1.5
xi = np.linspace(xmin, xmax, N)
yi = np.random.rand(N)

x_resample_res = 100
x_resample = np.linspace(xmin, xmax, x_resample_res)
resample_data = np.zeros_like(x_resample)
print(x_resample)


for i, res_point in enumerate(x_resample):
    distances = abs(res_point-xi)
    dist_index = np.where(distances >= 0)[0]
    for index in dist_index:
        resample_data[i] = yi[index]

plt.plot(xi, yi, 'bo')
plt.plot(x_resample, resample_data, 'yx')
plt.show()