import matplotlib.pyplot as plt
import numpy as np
import reliability.Reliability_testing
from reliability import Fitters, Distributions, Reliability_testing
from reliability.Utils import round_and_string
from abc import ABC, abstractmethod
from fracability.Entities import BaseEntity
from pandas import DataFrame
from scipy.stats import gaussian_kde
import scipy.stats as ss
import seaborn as sns
from copy import deepcopy

from fracability.utils import statistics

sns.set_theme()


class AbstractStatistics(ABC):

    def __init__(self, obj: BaseEntity = None):
        self._obj: BaseEntity = obj
        self._complete_lengths: list = []
        self._censored_lengths: list = []
        self._function_list: list = ['PDF', 'CDF', 'SF', 'HF', 'CHF']

        if obj is not None:
            self._lengths = obj.entity_df.loc[obj.entity_df['censored'] >= 0, 'length'].values
            self._data_adapter()

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

        return self._complete_lengths

    @complete_lengths.setter
    def complete_lengths(self, complete_length_list: list = []):
        self._complete_lengths = complete_length_list

    @property
    def censored_lengths(self):

        """
        This property returns or sets the list of censored length data of the fracture network

        :getter: Return the list of censored data
        :setter: Set the list of censored data
        :return:
        """

        return self._censored_lengths

    @censored_lengths.setter
    def censored_lengths(self, censored_length_list: list = []):
        self._censored_lengths = censored_length_list

    @property
    def fitter_list(self) -> list:

        """
        With the reliability package different fitters can be used. This property returns the list of
        available fitters.

        :return: A list of names of available fitters
        """

        return [i for i in dir(Fitters) if 'Fit_' in i]

    def _data_adapter(self):

        """
        Internal method used by the different Statistic classes to parse the entity_df of the input objects
        and separate censored form non censored data
        """

        entity_df = self._obj.entity_df
        self._complete_lengths = entity_df.loc[entity_df['censored'] == 0, 'length'].values
        self._censored_lengths = entity_df.loc[entity_df['censored'] == 1, 'length'].values


class NetworkFitter(AbstractStatistics):

    """
    Class used to fit a Fracture or Fracture network object
    """

    # Add bool do not consider censoring
    # add bool to plot pdf,cdf ,sf with no censoring

    def __init__(self, obj: BaseEntity = None):
        super().__init__(obj)

        self._fitter = None
        self._distribution = None
        self._accepted_fit: list = []
        self._rejected_fit: list = []
        self._test_dict: dict = {}

    @property
    def fitter(self):

        """
        With the reliability package different fitters can be used. This property returns or sets
        a given fitter.
        :getter: Returns the set reliability fitter
        :setter: Sets the type of reliability fitter
        :return:
        """

        return self._fitter

    @fitter.setter
    def fitter(self, reliability_fitter=None):
        self._fitter = reliability_fitter

    @property
    def dist(self):
        return self._distribution

    @dist.setter
    def dist(self, distribution=None):
        self._distribution = distribution

    def fit(self, fitter_name: str = '',censored_data: bool =True):

        """
        Fit the data of the entity_df using one of the fitters available in reliability
        :param fitter_name: Name of the fitter
        :return:
        """

        if fitter_name in self.fitter_list:
            fitter = getattr(Fitters, fitter_name)
            if censored_data:
                rel_fitter = fitter(failures=self.complete_lengths, right_censored=self.censored_lengths,
                                    show_probability_plot=False, print_results=False)
            else:
                rel_fitter = fitter(failures=self.lengths, show_probability_plot=False, print_results=False)

            self.fitter = rel_fitter
            self.dist = rel_fitter.distribution
        else:
            print(f'The fitter {fitter_name} is not available')

    def get_fit_parameters(self) -> DataFrame:

        """
        Get the parameters of the computed fit. This method returns a pandas dataframe summarizing the
        parameters of the chosen fit
        :return: Pandas DataFrame
        """
        return self.fitter.results

    @property
    def accepted_fit(self):
        return self._accepted_fit

    @accepted_fit.setter
    def accepted_fit(self, fitter_list: list = None):
        self._accepted_fit = fitter_list

    @property
    def rejected_fit(self):
        return self._rejected_fit

    @rejected_fit.setter
    def rejected_fit(self, fitter_list: list = None):
        self._rejected_fit = fitter_list

    @property
    def test_parameters(self):
        return self._test_dict

    @test_parameters.setter
    def test_parameters(self, res_dict: dict = None):
        self._test_dict = res_dict

    def summary_plot(self, x_min: float = 0.0, x_max: float = None, res: int = 200):

        """
        Summarize PDF, CDF and SF functions and display mean, std, var, median, mode, 5th and 95th percentile all
        in a single plot.
        A range of values and the resolution can be defined with the x_min, x_max and res parameters.

        Parameters
        -------
        x_min: Lower value of the range. By default is set to 0

        x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

        res: Point resolution between x_min and x_max. By default is set to 1000
        """

        if x_max is None:
            x_max = max(self._obj.entity_df['length'])

        x_vals = np.linspace(x_min, x_max, res)

        fig = plt.figure(num='Summary plot', figsize=(13, 7))
        fig.text(0.5, 0.02, 'Length [m]', ha='center')
        fig.text(0.5, 0.95, self.dist.name2, ha='center')
        fig.text(0.04, 0.5, 'Density', va='center', rotation='vertical')

        for i, name in enumerate(self._function_list[:3]):
            func = getattr(self.dist, name)

            y_vals = func(xvals=x_vals, show_plot=False)
            plt.subplot(2, 2, i+1)
            plt.plot(x_vals, y_vals)
            if name == 'CDF':
                xvals, ecdf = statistics.ecdf(self.complete_lengths, self.censored_lengths)
                plt.step(xvals, ecdf, 'r-')
            plt.title(name)
            plt.grid(True)

        plt.subplot(2, 2, i+2)
        plt.axis("off")
        plt.ylim([0, 8])
        plt.xlim([0, 10])
        dec = 4

        text_mean = f'Mean = {round_and_string(self.dist.mean, dec)}'
        text_std = f'Std = {round_and_string(self.dist.standard_deviation, dec)}'
        text_var = f'Var = {round_and_string(self.dist.variance, dec)}'
        text_median = f'Median = {round_and_string(self.dist.median, dec)}'
        text_mode = f'Mode = {round_and_string(self.dist.mode, dec)}'
        text_b5 = f'5th Percentile = {round_and_string(self.dist.b5, dec)}'
        text_b95 = f'95th Percentile = {round_and_string(self.dist.b95, dec)}'

        plt.text(0, 7.5, 'Summary table')
        plt.text(0, 6.5, text_mean)
        plt.text(0, 5.5, text_median)
        plt.text(0, 4.5, text_mode)
        plt.text(0, 3.5, text_b5)
        plt.text(0, 2.5, text_b95)
        plt.text(0, 1.5, text_std)
        plt.text(0, 0.5, text_var)

        plt.text(6, 7.5, 'Test results:')

        if self.test_parameters:

            text_result = self.test_parameters['Result']
            text_crit_val = f'KS critical value = {round_and_string(self.test_parameters["crit_val"])}'
            text_ks_val = f'KS statistic = {round_and_string(self.test_parameters["KS_stat"])}'

            plt.text(8.5, 7.5, text_result)
            plt.text(6, 6.5, text_crit_val)
            plt.text(6, 5.5, text_ks_val)

        else:
            plt.text(6, 6.5, 'No test has been executed')

        plt.show()

    def plot_function(self,
                      func_name: str,
                      x_min: float = 0.0,
                      x_max: float = None,
                      res: int = 200):
        
        """
        Plot PDF, CDF or SF functions in a range of x values and with a given resolution.

        Parameters
        -------
        func_name: Name of the function to plot. Use the fitter_list method to display the available methods.

        x_min: Lower value of the range. By default it is set to 0

        x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

        res: Point resolution between x_min and x_max. By default is set to 1000

        Notes
        -------
        Each plot is created in a separate figure with the name associated to the given funtion
        """

        if x_max is None:
            x_max = self._lengths.max()*10

        x_vals = np.linspace(x_min, x_max, res)

        func = getattr(self.dist, func_name) # get the specific function (PDF, CDF, SF)
        y_vals = func(xvals=x_vals, show_plot=False)


        fig = plt.figure(num=func_name)
        plt.plot(x_vals, y_vals, 'b-', label='Theoretical cdf')

        if func_name == 'CDF':
            xval, ecdf = statistics.ecdf(self.complete_lengths,self.censored_lengths)
            plt.step(xval, ecdf, 'r-', label='Empirical cdf')
        plt.title(func_name)
        plt.xlabel('Length [m]')
        plt.ylabel('Function response')
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_kde(self, n_bins: int = 25, x_min: float = 0.0, x_max: float = None, res: int = 1000):

        """
        Plot the Kernel Density Estimation PDF function togather with the data histogram

        Parameters
        -------
        n_bins: Number of histogram bins

        x_min: Lower value of the range. By default is set to 0

        x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

        res: Point resolution between x_min and x_max. By default is set to 1000

        """

        data = self._lengths

        if x_max is None:
            x_max = self._lengths.max()

        x_vals = np.linspace(x_min, x_max, res)

        pdf_kde = gaussian_kde(data).evaluate(x_vals)

        fig = plt.figure(num='Gaussian KDE estimation')
        plt.hist(data, density=True, bins=15,label='Data')
        plt.plot(x_vals, pdf_kde, label='Gaussian KDE')

        plt.title('Gaussian KDE estimation')
        plt.xlabel('Length [m]')
        plt.ylabel('Function response')
        plt.grid(True)
        plt.show()

    def find_best_distribution(self):
        test_list = ['Fit_Exponential_1P',
                     'Fit_Exponential_2P',
                     'Fit_Gamma_2P',
                     'Fit_Loglogistic_2P',
                     'Fit_Lognormal_2P',
                     'Fit_Normal_2P']

        for dist in test_list:

            self.fit(dist)
            fit_dist = self.dist
            data = self.lengths

            cdf = fit_dist.CDF(show_plot=False)
            test = ss.kstest(data, ss.lognorm.cdf,args = (fit_dist))
            print(f'{dist}: {test}')
            # reliability.Reliability_testing.KStest(distribution=fit_dist,
            #                                               data=data, print_results=True,
            #                                               show_plot=True)
            #
            # plt.show()
            #
            # self.test_parameters = {'Result': test.hypothesis,
            #                         'crit_val': test.KS_critical_value,
            #                         'KS_stat': test.KS_statistic
            #                         }
            #
            # if test.hypothesis == 'ACCEPT':
            #     self.accepted_fit.append(deepcopy(self))
            # else:
            #     self.rejected_fit.append(deepcopy(self))




