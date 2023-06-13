import matplotlib.pyplot as plt
import numpy as np
from reliability import Fitters
from reliability.Utils import round_and_string
from abc import ABC, abstractmethod
from fracability.Entities import BaseEntity
from pandas import DataFrame
from scipy.stats import gaussian_kde
import scipy.stats as ss
import seaborn as sns
import ast
from copy import deepcopy

from fracability.utils import statistics

sns.set_theme()


class AbstractStatistics(ABC):

    def __init__(self, obj: BaseEntity = None):
        self._obj: BaseEntity = obj

        self._data: ss.CensoredData
        self._lengths: np.array

        self._function_list: list = ['pdf', 'cdf', 'sf', 'hf', 'chf']

        if obj is not None:
            self._lengths = obj.entity_df.loc[obj.entity_df['censored'] >= 0, 'length'].values
            entity_df = self._obj.entity_df
            self._complete_lengths = entity_df.loc[entity_df['censored'] == 0, 'length'].values
            self._censored_lengths = entity_df.loc[entity_df['censored'] == 1, 'length'].values

            self._data = ss.CensoredData(uncensored=self._complete_lengths, right=self._censored_lengths)

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
    def complete_lengths(self):

        """
        This property returns or sets the list of non-censored length data of the fracture network

        :getter: Return the list of non-censored data
        :setter: Set the list of non-censored data
        """

        return self._data.__dict__['_uncensored']

    @complete_lengths.setter
    def complete_lengths(self, complete_length_list: list = []):
        self._data = ss.CensoredData(uncensored=complete_length_list, right=self.censored_lengths)

    @property
    def censored_lengths(self):

        """
        This property returns or sets the list of censored length data of the fracture network

        :getter: Return the list of censored data
        :setter: Set the list of censored data
        :return:
        """

        return self._data.__dict__['_right']

    @censored_lengths.setter
    def censored_lengths(self, censored_length_list: list = []):
        self._data = ss.CensoredData(uncensored=self.complete_lengths, right=censored_length_list)

    @property
    def ecdf(self):
        return ss.ecdf(self._data)


class NetworkFitter(AbstractStatistics):

    """
    Class used to fit a Fracture or Fracture network object
    """

    # Add bool do not consider censoring
    # add bool to plot pdf,cdf ,sf with no censoring

    def __init__(self, obj: BaseEntity = None):
        super().__init__(obj)

        self._parameters = None
        self._distribution = None
        self._accepted_fit: list = []
        self._rejected_fit: list = []
        self._fit_dataframe: DataFrame = DataFrame(columns=['name', 'AICc', 'BIC', 'log_likelyhood', 'distribution', 'params'])

    @property
    def dist(self):
        return self._distribution

    @dist.setter
    def dist(self, distribution=None):
        self._distribution = distribution

    def fit(self, distribution_name: str = '', censored_data: bool = True):

        """
        Fit the data of the entity_df using one of the fitters available in reliability
        :param distribution_name: Name of the distribution
        :param censored_data:
        :return:
        """
        if distribution_name != '':
            self._distribution = getattr(ss, distribution_name)
        if censored_data:
            if distribution_name == 'norm' or distribution_name == 'logistic':
                params = self._distribution.fit(self._data)
            else:
                params = self._distribution.fit(self._data, floc=0)

            log_f = self._distribution .logpdf(self.complete_lengths, *params)
            log_r = self._distribution .logsf(self.censored_lengths, *params)

        else:
            if distribution_name == 'norm' or distribution_name == 'logistic':
                params = self._distribution .fit(self.lengths)
            else:
                params = self._distribution .fit(self.lengths, floc=0)

            log_f = self._distribution .logpdf(self.lengths, *params)
            log_r = 0

        LL_f = log_f.sum()
        LL_rc = log_r.sum()

        log_likelyhood = LL_f+LL_rc

        LL2 = -2*log_likelyhood


        k = len(params)
        n = len(self.complete_lengths)+len(self.censored_lengths)

        AICc = 2*k + LL2 + (2 * k**2 + 2*k)/(n - k - 1)
        BIC = np.log(n)*k + LL2

        self._fit_dataframe.loc[len(self._fit_dataframe)] = [distribution_name,
                                                             AICc, BIC,
                                                             log_likelyhood, self._distribution, str(params)]

    def get_fit_parameters(self, distribution_name: str = None) -> DataFrame:

        """
        Get the parameters of the computed fit. This method returns a pandas dataframe summarizing the
        parameters of the chosen distribution if the distribution name is not specified.
        :return: Pandas DataFrame
        """
        print(self.fit_records)
        if distribution_name:

            parameters = self.fit_records.loc[self.fit_records['name'] == distribution_name, 'params'].values[0]
            return ast.literal_eval(parameters)

        else:
            return self._fit_dataframe[['name', 'params']]

    @property
    def fit_records(self) -> DataFrame:

        """ Return the sorted fit dataframe"""

        return self._fit_dataframe.sort_values(by='AICc', ignore_index=True)

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
        #             xvals, ecdf = statistics.ecdf(self.complete_lengths, self.censored_lengths)
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
    #         xval, ecdf = statistics.ecdf(self.complete_lengths,self.censored_lengths)
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