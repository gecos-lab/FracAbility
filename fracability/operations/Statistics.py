import numpy as np

from abc import ABC

from pandas import DataFrame
import scipy.stats as ss
from scipy.optimize import minimize
import ast


from fracability.AbstractClasses import BaseEntity


class NetworkData:
    """ Class used to represent fracture or fracture network data.
    It acts as a wrapper for the scipy CensoredData class
    """

    def __init__(self, obj: BaseEntity = None):
        self._obj: BaseEntity = obj

        self._data: ss.CensoredData
        self._lengths: np.array

        self._function_list: list = ['pdf', 'cdf', 'sf', 'hf', 'chf']

        if obj is not None:
            entity_df = self._obj.entity_df

            self.lengths = entity_df.loc[entity_df['censored'] >= 0, 'length'].values
            non_censored_lengths = entity_df.loc[entity_df['censored'] == 0, 'length'].values
            censored_lengths = entity_df.loc[entity_df['censored'] == 1, 'length'].values

            self.data = ss.CensoredData(uncensored=non_censored_lengths, right=censored_lengths)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: ss.CensoredData):
        self._data = data

    @property
    def lengths(self):

        """
        This property returns or sets the complete list of length data for the fracture network

        :getter: Return the complete list of lengths
        :setter: Set the complete list of lengths
        """

        return self._lengths

    @lengths.setter
    def lengths(self, length_list: list = None):
        self._lengths = length_list

    @property
    def non_censored_lengths(self):

        """
        This property returns or sets the list of non-censored length data of the fracture network

        :getter: Return the list of non-censored data
        :setter: Set the list of non-censored data
        """

        return self.data.__dict__['_uncensored']

    @non_censored_lengths.setter
    def non_censored_lengths(self, complete_length_list: list = []):
        self.data = ss.CensoredData(uncensored=complete_length_list, right=self.censored_lengths)

    @property
    def censored_lengths(self):

        """
        This property returns or sets the list of censored length data of the fracture network

        :getter: Return the list of censored data
        :setter: Set the list of censored data
        :return:
        """

        return self.data.__dict__['_right']

    @censored_lengths.setter
    def censored_lengths(self, censored_length_list: list = []):
        self.data = ss.CensoredData(uncensored=self.non_censored_lengths, right=censored_length_list)

    @property
    def function_list(self):
        return self._function_list


class NetworkDistribution:
    """
    Class used to represent a fracture or fracture network length distribution. It is essentially a wrapper for the
    scipy rv distributions.
    """

    def __init__(self, obj: ss.rv_continuous = None, parameters: tuple = None, fit_data: NetworkData = None):

        self._distribution = obj.freeze(*parameters)
        self.fit_data = fit_data

    @property
    def distribution(self):
        return self._distribution

    @distribution.setter
    def distribution(self, distribution: ss.rv_continuous = None):
        self._distribution = distribution

    @property
    def distribution_name(self):
        return self.distribution.dist.name

    @property
    def distribution_parameters(self):
        return self.distribution.args

    @property
    def mean(self):
        return self.distribution.mean()

    @property
    def mode(self):
        return minimize(lambda x: -self.distribution.pdf(x), np.ceil(self.distribution_parameters[-1])).x

    @property
    def median(self):
        return self.distribution.median()

    @property
    def var(self):
        return self.distribution.var()

    @property
    def std(self):
        return self.distribution.std()

    @property
    def b5(self):
        return self.distribution.ppf(0.05)

    @property
    def b95(self):
        return self.distribution.ppf(0.95)

    @property
    def ecdf(self):
        return ss.ecdf(self.fit_data.data)

    @property
    def log_likelihood(self):

        log_f = self.log_pdf(self.fit_data.non_censored_lengths)
        log_r = self.log_sf(self.fit_data.censored_lengths)

        LL_f = log_f.sum()
        LL_rc = log_r.sum()

        return LL_f + LL_rc

    @property
    def AICc(self):

        LL2 = -2 * self.log_likelihood

        k = len(self.distribution_parameters)
        n = len(self.fit_data.non_censored_lengths) + len(self.fit_data.censored_lengths)

        AICc = 2 * k + LL2 + (2 * k ** 2 + 2 * k) / (n - k - 1)
        return AICc

    @property
    def BIC(self):

        LL2 = -2 * self.log_likelihood

        k = len(self.distribution_parameters)
        n = len(self.fit_data.non_censored_lengths) + len(self.fit_data.censored_lengths)

        BIC = np.log(n)*k + LL2
        return BIC

    def log_pdf(self, x_values: np.array = None):

        if x_values.any():
            return self.distribution.logpdf(x_values)
        else:
            return np.array([0])

    def log_sf(self, x_values: np.array = None):
        if x_values.any():
            return self.distribution.logsf(x_values)
        else:
            return np.array([0])



class NetworkFitter:

    """
    Class used to fit a Fracture or Fracture network object
    """

    # Add bool do not consider censoring
    # add bool to plot pdf,cdf, sf with no censoring

    def __init__(self, obj: BaseEntity = None):

        self.net_data = NetworkData(obj)
        self._accepted_fit: list = []
        self._rejected_fit: list = []
        self._fit_dataframe: DataFrame = DataFrame(columns=['name', 'AICc', 'BIC',
                                                            'log_likelihood', 'distribution', 'params'])

    def fit(self, distribution_name: str):

        """
        Fit the data of the entity_df using scipy available distributions
        :param distribution_name: Name of the distribution
        :param censored_data:
        :return:
        """

        distribution = getattr(ss, distribution_name)

        if self.net_data.censored_lengths.any():
            if distribution_name == 'norm' or distribution_name == 'logistic':
                params = distribution.fit(self.net_data.data)
            else:
                params = distribution.fit(self.net_data.data, floc=0)

        else:
            if distribution_name == 'norm' or distribution_name == 'logistic':
                params = distribution.fit(self.net_data.lengths)
            else:
                params = distribution.fit(self.net_data.lengths, floc=0)

        distribution = NetworkDistribution(distribution, params, self.net_data)

        AICc = distribution.AICc
        BIC = distribution.BIC
        log_likelihood = distribution.log_likelihood

        self._fit_dataframe.loc[len(self._fit_dataframe)] = [distribution_name,
                                                             AICc, BIC,
                                                             log_likelihood, distribution, str(params)]

    def get_fit_parameters(self, distribution_names: list = None) -> list:

        """
        Get the parameters of the computed fit(s)
        :return: Pandas DataFrame
        """
        if distribution_names is None:
            distribution_names = self.fit_records['name'].tolist()

        parameter_list = []

        for name in distribution_names:
            parameters = self.fit_records.loc[self.fit_records['name'] == name, 'params'].values[0]
            parameter_list.append(ast.literal_eval(parameters))

        return parameter_list

    def get_fit_distribution(self, distribution_names: list = None) -> list:

        if distribution_names is None:
            distribution_names = self.fit_records['name'].tolist()

        distribution_list = []

        for name in distribution_names:
            distribution = self.fit_records.loc[self.fit_records['name'] == name, 'distribution'].values[0]
            distribution_list.append(distribution)

        return distribution_list

    @property
    def fit_records(self) -> DataFrame:

        """ Return the sorted fit dataframe"""

        return self._fit_dataframe.sort_values(by='BIC', ignore_index=True)

    def best_fit(self):

        df = self.fit_records

        return df.loc[0]

    def rejected_fit(self):

        df = self.fit_records

        return df.loc[1:]

    def find_best_distribution(self, distribution_list: list = None):

        if distribution_list is None:

            distribution_list = ['lognorm',
                                 'norm',
                                 'expon',
                                 'burr12',
                                 'gamma',
                                 'logistic']

        for distribution in distribution_list:
            self.fit(distribution)

        return self.best_fit()

        # fig1 = plt.figure(num='CDF plots', figsize=(13, 7))
        # fig2 = plt.figure(num='Histograms', figsize=(13, 7))
        # for i in sorted.index:
        #
        #     distr = sorted.loc[i, 'distr']
        #     params = ast.literal_eval(sorted.loc[i, 'params'])
        #     fitter_name = sorted.loc[i, 'name']
        #     aicc = sorted.loc[i, 'AICc']
        #
        #     cdf = distr.cdf(ecdf.quantiles, *params)
        #     pdf = distr.pdf(ecdf.quantiles, *params)
        #
        #     plt.figure(num='CDF plots')
        #     plt.tight_layout()
        #     plt.subplot(2, 3, i + 1)
        #     # if i//3 < 1:
        #     #     plt.tick_params(labelbottom=False)
        #     # if i%3 > 0:
        #     #     plt.tick_params(labelleft=False)
        #     plt.title(f'{fitter_name}   AICc: {np.round(aicc, 3)}')
        #     plt.plot(ecdf.quantiles, ecdf.probabilities, 'b-', label='Empirical CDF')
        #     plt.plot(ecdf.quantiles, cdf, 'r-', label=f'{fitter_name} CDF')
        #     plt.legend()
        #
        #     plt.figure('Histograms')
        #     plt.subplot(2, 3, i + 1)
        #     plt.title(f'{fitter_name}   AICc: {np.round(aicc, 3)}')
        #     sns.histplot(lengths, stat='density', bins=50)
        #     sns.lineplot(x=ecdf.quantiles, y=pdf, label=f'{fitter_name} PDF', color='r')
        #     plt.legend()
        #
        # plt.show()

    # def summary_plot(self, x_min: float = 0.0, x_max: float = None, res: int = 200):
        #
        #     """
        #     Summarize PDF, CDF and SF functions and display mean, std, var, median, mode, 5th and 95th percentile all
        #     in a single plot.
        #     A range of values and the resolution can be defined with the x_min, x_max and res parameters.
        #
        #     Parameters
        #     -------
        #     x_min: Lower value of the range. By default is set to 0
        #
        #     x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default
        #
        #     res: Point resolution between x_min and x_max. By default is set to 1000
        #     """
        #
        #     if x_max is None:
        #         x_max = max(self._obj.entity_df['length'])
        #
        #     x_vals = np.linspace(x_min, x_max, res)
        #
        #     fig = plt.figure(num='Summary plot', figsize=(13, 7))
        #     fig.text(0.5, 0.02, 'Length [m]', ha='center')
        #     fig.text(0.5, 0.95, self.dist.name2, ha='center')
        #     fig.text(0.04, 0.5, 'Density', va='center', rotation='vertical')
        #
        #     for i, name in enumerate(self._function_list[:3]):
        #         func = getattr(self.dist, name)
        #
        #         y_vals = func(xvals=x_vals, show_plot=False)
        #         plt.subplot(2, 2, i+1)
        #         plt.plot(x_vals, y_vals)
        #         if name == 'CDF':
        #             xvals, ecdf = statistics.ecdf(self.non_censored_lengths, self.censored_lengths)
        #             plt.step(xvals, ecdf, 'r-')
        #         plt.title(name)
        #         plt.grid(True)
        #
        #     plt.subplot(2, 2, i+2)
        #     plt.axis("off")
        #     plt.ylim([0, 8])
        #     plt.xlim([0, 10])
        #     dec = 4
        #
        #     text_mean = f'Mean = {round_and_string(self.dist.mean, dec)}'
        #     text_std = f'Std = {round_and_string(self.dist.standard_deviation, dec)}'
        #     text_var = f'Var = {round_and_string(self.dist.variance, dec)}'
        #     text_median = f'Median = {round_and_string(self.dist.median, dec)}'
        #     text_mode = f'Mode = {round_and_string(self.dist.mode, dec)}'
        #     text_b5 = f'5th Percentile = {round_and_string(self.dist.b5, dec)}'
        #     text_b95 = f'95th Percentile = {round_and_string(self.dist.b95, dec)}'
        #
        #     plt.text(0, 7.5, 'Summary table')
        #     plt.text(0, 6.5, text_mean)
        #     plt.text(0, 5.5, text_median)
        #     plt.text(0, 4.5, text_mode)
        #     plt.text(0, 3.5, text_b5)
        #     plt.text(0, 2.5, text_b95)
        #     plt.text(0, 1.5, text_std)
        #     plt.text(0, 0.5, text_var)
        #
        #     plt.text(6, 7.5, 'Test results:')
        #
        #     if self.test_parameters:
        #
        #         text_result = self.test_parameters['Result']
        #         text_crit_val = f'KS critical value = {round_and_string(self.test_parameters["crit_val"])}'
        #         text_ks_val = f'KS statistic = {round_and_string(self.test_parameters["KS_stat"])}'
        #
        #         plt.text(8.5, 7.5, text_result)
        #         plt.text(6, 6.5, text_crit_val)
        #         plt.text(6, 5.5, text_ks_val)
        #
        #     else:
        #         plt.text(6, 6.5, 'No test has been executed')
        #
        #     plt.show()

    # def plot_function(self,
    #                   func_name: str,
    #                   x_min: float = 0.0,
    #                   x_max: float = None,
    #                   res: int = 200):
    #
    #     """
    #     Plot PDF, CDF or SF functions in a range of x values and with a given resolution.
    #
    #     Parameters
    #     -------
    #     func_name: Name of the function to plot. Use the fitter_list method to display the available methods.
    #
    #     x_min: Lower value of the range. By default it is set to 0
    #
    #     x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default
    #
    #     res: Point resolution between x_min and x_max. By default is set to 1000
    #
    #     Notes
    #     -------
    #     Each plot is created in a separate figure with the name associated to the given funtion
    #     """
    #
    #     if x_max is None:
    #         x_max = self._lengths.max()*10
    #
    #     x_vals = np.linspace(x_min, x_max, res)
    #
    #     func = getattr(self.dist, func_name) # get the specific function (PDF, CDF, SF)
    #     y_vals = func(xvals=x_vals, show_plot=False)
    #
    #
    #     fig = plt.figure(num=func_name)
    #     plt.plot(x_vals, y_vals, 'b-', label='Theoretical cdf')
    #
    #     if func_name == 'CDF':
    #         xval, ecdf = statistics.ecdf(self.non_censored_lengths,self.censored_lengths)
    #         plt.step(xval, ecdf, 'r-', label='Empirical cdf')
    #     plt.title(func_name)
    #     plt.xlabel('Length [m]')
    #     plt.ylabel('Function response')
    #     plt.grid(True)
    #     plt.legend()
    #     plt.show()

    # def plot_kde(self, n_bins: int = 25, x_min: float = 0.0, x_max: float = None, res: int = 1000):
    #
    #     """
    #     Plot the Kernel Density Estimation PDF function togather with the data histogram
    #
    #     Parameters
    #     -------
    #     n_bins: Number of histogram bins
    #
    #     x_min: Lower value of the range. By default is set to 0
    #
    #     x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default
    #
    #     res: Point resolution between x_min and x_max. By default is set to 1000
    #
    #     """
    #
    #     data = self._lengths
    #
    #     if x_max is None:
    #         x_max = self._lengths.max()
    #
    #     x_vals = np.linspace(x_min, x_max, res)
    #
    #     pdf_kde = gaussian_kde(data).evaluate(x_vals)
    #
    #     fig = plt.figure(num='Gaussian KDE estimation')
    #     plt.hist(data, density=True, bins=15,label='Data')
    #     plt.plot(x_vals, pdf_kde, label='Gaussian KDE')
    #
    #     plt.title('Gaussian KDE estimation')
    #     plt.xlabel('Length [m]')
    #     plt.ylabel('Function response')
    #     plt.grid(True)
    #     plt.show()