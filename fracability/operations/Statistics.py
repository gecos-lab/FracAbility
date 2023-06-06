import matplotlib.pyplot as plt
import numpy as np
from reliability import Fitters, Distributions, Reliability_testing
from reliability.Utils import round_and_string
from abc import ABC, abstractmethod
from fracability.Entities import BaseEntity
from pandas import DataFrame
from scipy.stats import gaussian_kde
import seaborn as sns

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
        This property returns or sets the list of non-censored length data of the fracture network

        :getter: Return the list of non-censored data
        :setter: Set the list of non-censored data
        """

        return self._complete_lengths

    @lengths.setter
    def lengths(self, length_list: list = []):
        self._complete_lengths = length_list

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

    def fit(self, fitter_name: str = ''):

        """
        Fit the data of the entity_df using one of the fitters available in reliability
        :param fitter_name: Name of the fitter
        :return:
        """

        if fitter_name in self.fitter_list:
            rel_fitter = getattr(Fitters, fitter_name)
            self.fitter = rel_fitter(failures=self.lengths, right_censored=self.censored_lengths,
                                     show_probability_plot=False, print_results=False)
        else:
            print(f'The fitter {fitter_name} is not available')

    def get_fit_parameters(self) -> DataFrame:

        """
        Get the parameters of the computed fit. This method returns a pandas dataframe summarizing the
        parameters of the chosen fit
        :return: Pandas DataFrame
        """
        return self.fitter.results

    def summary_plot(self, x_min: float = 0.0, x_max: float = None, res: int = 1000):

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
            x_max = max(self._obj.entity_df['length'])*10

        x_vals = np.linspace(x_min, x_max, res)

        fig = plt.figure(num='Summary plot', figsize=(9, 7))
        fig.text(0.5, 0.04, 'Length [m]', ha='center')
        fig.text(0.04, 0.5, 'Function response', va='center', rotation='vertical')

        for i, name in enumerate(self._function_list[:3]):
            func = getattr(self.fitter.distribution, name)
            y_vals = func(xvals=x_vals, show_plot=False)
            plt.subplot(2, 2, i+1)
            plt.plot(x_vals, y_vals)
            plt.title(name)
            plt.grid(True)

        plt.subplot(2, 2, i+2)
        plt.axis("off")
        plt.ylim([0, 7])
        plt.xlim([0, 7])
        dec = 4
        text_mean = f'Mean = {round_and_string(self.fitter.distribution.mean, dec)}'
        text_std = f'Std = {round_and_string(self.fitter.distribution.standard_deviation, dec)}'
        text_var = f'Var = {round_and_string(self.fitter.distribution.variance, dec)}'
        text_median = f'Median = {round_and_string(self.fitter.distribution.median, dec)}'
        text_mode = f'Mode = {round_and_string(self.fitter.distribution.mode, dec)}'
        text_b5 = f'5th Percentile = {round_and_string(self.fitter.distribution.b5, dec)}'
        text_b95 = f'95th Percentile = {round_and_string(self.fitter.distribution.b95, dec)}'

        plt.text(0, 7, 'Summary table')
        plt.text(0, 6, text_mean)
        plt.text(0, 5, text_median)
        plt.text(0, 4, text_mode)
        plt.text(0, 3, text_b5)
        plt.text(0, 2, text_b95)
        plt.text(0, 1, text_std)
        plt.text(0, 0, text_var)

        plt.show()

    def plot_function(self, func_name: str, x_min: float = 0.0, x_max: float = None, res: int = 1000):
        
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

        func = getattr(self.fitter.distribution, func_name)
        y_vals = func(xvals=x_vals, show_plot=False)

        fig = plt.figure(num=func_name)
        plt.plot(x_vals, y_vals)
        plt.title(func_name)
        plt.xlabel('Length [m]')
        plt.ylabel('Function response')
        plt.grid(True)
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


class NetworkTester(AbstractStatistics):
    """
    Class used to test and define the best fitter using Kolmogorov-Smirnov test.
    """