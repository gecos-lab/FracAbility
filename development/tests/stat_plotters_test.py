import numpy as np
import scipy.stats as ss
import matplotlib.pyplot as plt
import seaborn as sns
from fracability.utils.general_use import KM, setFigLinesBW
import pandas as pd
from adjustText import adjust_text


def ecdf_find_x(ecdf_prob, y_values):

    x_values = []
    for y in y_values:
        mask = ecdf < y
        last_true = np.count_nonzero(mask) - 1
        first_false = last_true + 1
        if last_true < 0:
            int_x = samples[0]
        elif first_false == len(ecdf_prob):
            int_x = samples[-1]
        else:
            int_x = np.mean([samples[last_true], samples[first_false]])

        x_values.append(np.round(int_x, 2))
    return x_values


# data = pd.read_csv('Salza/output/csv/Fractures_2.csv', sep=';')
# data = pd.read_csv('../Pontrelli/output/csv/Fractures_1.csv', sep=',')
# data.sort_values(by='length', inplace=True)
# samples = data['length'].values
# delta = 1-data['censored'].copy().values
#
# non_censored = data.loc[data['censored'] == 0, 'length'].values
# censored = data.loc[data['censored'] == 1, 'length'].values
#
# censored_data = ss.CensoredData(uncensored=non_censored, right=censored)
#
# model_dict = {}
#
# model_list = ['lognorm', 'norm', 'gamma', 'expon', 'powerlaw', 'weibull_min']
#
# for model in model_list:
#     dist = getattr(ss, model)
#     if model == 'norm' or model == 'logistic':
#         params = dist.fit(censored_data)
#     else:
#         params = dist.fit(censored_data, floc=0)
#
#     model_dict[dist(*params)] = model


number_of_samples = 1000
samples = np.genfromtxt('samples.csv')
delta = np.ones(len(samples))
samples.sort()
mu = np.arange(-2, 3, 2)
exp_dist = ss.expon(scale=1)
log_dist = ss.lognorm(loc=0, s=1)


ecdf = KM(samples, samples, delta)
model_dict = {}

for m in mu:
    dist = ss.norm(m, 1)
    model_dict[dist] = f'N ({m}, 1)'

model_dict[exp_dist] = f'E(1)'
model_dict[log_dist] = f'Ln(0, 1)'


sns.histplot(samples)
plt.title(f'Frequency of {number_of_samples} random samples\ndrawn from a standard normal distribution')
plt.xlabel('X')
# plt.show()


fig = plt.figure(num=f'CDF comparison plot', figsize=(13, 7))

for dist in model_dict.keys():
    plt.plot(samples, dist.cdf(samples), label=f'{model_dict[dist]} CDF')


setFigLinesBW(fig)

plt.plot(samples, ecdf, drawstyle='steps', color='r', label='ECDF')
plt.legend()
plt.title('CDF plot of the tested models')
plt.xlabel('X')
plt.ylabel(r'Z=$F_{x}$(X)')
# plt.show()


fig = plt.figure(num=f'PIT comparison plot', figsize=(13, 7))
ax = plt.subplot(111)

for dist in model_dict.keys():
    cdf = dist.cdf(samples)
    pit_cdf = KM(cdf, cdf, delta)
    ax.plot(cdf, pit_cdf, label=f'{model_dict[dist]} PIT')


setFigLinesBW(fig)

ax.plot([0, 1], [0, 1], color='r', label='U (0,1)')
ax.set_xlabel(r'Z=$F_{x}$(X)')
ax.set_ylabel('Cumulative frequency')


n_ticks = 6
x_ticks = np.linspace(0, 1, n_ticks)
# x_ticks = np.array([0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1])

xticks_labels = ecdf_find_x(ecdf_prob=ecdf, y_values=x_ticks)

ax2 = ax.twiny()
ax2.plot(x_ticks, [0]*len(x_ticks), visible=False)
ax2.spines['top'].set_position(('axes', -0.11))
ax2.spines['top'].set_visible(False)
ax2.spines['bottom'].set_position(('axes', -0.05))
ax2.spines['bottom'].set_visible(True)
ax2.set_xticks(x_ticks)
ax2.set_xticklabels(xticks_labels)

ax2.annotate(f'Reference length [m]', (-0.01, 0.5), ha='right', va='center', xycoords=ax2.spines['bottom'])

ax.legend()
plt.tick_params(which='both', direction='inout', bottom=True, top=False, length=6)
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
# plt.show()

fig = plt.figure(num=f'Tick plot', figsize=(13, 7))
ax = plt.subplot(111)

xticks_labels = ecdf_find_x(ecdf_prob=ecdf, y_values=x_ticks)

for i, model in enumerate(model_dict.keys()):
    y = i
    ax.axhline(y=y, color='k')
    values_labels = model.cdf(xticks_labels)
    for value, x in zip(values_labels, xticks_labels):
        point = ax.plot(value, y, 'k|', markersize=12, linewidth=1)
        ax.annotate(xy=(0.5, -1.1), text=f'{x}', ha='center', va='center', xycoords=point[0], annotation_clip=True)

plt.title('Tick plot')
ax.set_xlim(-0.1, 1.1)
ax.set_ylim(bottom=-0.5)
ax.set_yticks(range(len(model_dict.values())))
ax.set_yticklabels(model_dict.values())
ax.set_xticks(x_ticks)
ax.set_xticklabels(xticks_labels)
ax.set_xlabel('Length[m]')
ax.annotate(f'Kaplan-Meier', (-0.01, 0.5), ha='right', va='center', xycoords=ax.spines['bottom'])

ax.grid('y')
ax.spines[['left', 'top', 'right']].set_visible(False)
plt.show()
