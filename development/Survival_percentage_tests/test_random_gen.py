"""
Test for random generations with seed.
Taken from https://stackoverflow.com/a/63980788
"""

from numpy.random import Generator, PCG64
from scipy.stats import binom, norm

n, p, size, seed = 10, 0.5, 10, 12345

# Case 1 : Scipy uses some default Random Generator
numpy_randomGen = Generator(PCG64(seed))
scipy_randomGen = norm
print(scipy_randomGen.rvs(n, p, size=size))
# print(numpy_randomGen.binomial(n, p, size))
# prints
# [6 6 5 4 6 6 8 6 6 4]
# [4 4 6 6 5 4 5 4 6 7]
# NOT DESIRABLE as we don't have control over the seed of Scipy random number generation


# Case 2 : Scipy uses same seed and Random generator (new object though)
scipy_randomGen.random_state=Generator(PCG64(seed))
numpy_randomGen = Generator(PCG64(seed))
print(scipy_randomGen.rvs(n, p, size=size))
# print(numpy_randomGen.binomial(n, p, size=size))
# prints
# [4 4 6 6 5 4 5 4 6 7]
# [4 4 6 6 5 4 5 4 6 7]
    # This experiment is using same sequence of random numbers, one is being used by Scipy
# and other by Numpy. NOT DESIRABLE as we don't want repetition of some random
# stream in same experiment.


# Case 3 (IMP) : Scipy uses an existing Random Generator which can being passed to Scipy based
# random generator object
numpy_randomGen = Generator(PCG64(seed))
# scipy_randomGen.random_state=numpy_randomGen
print(scipy_randomGen.rvs(n, p, size=size, random_state=numpy_randomGen))
# print(numpy_randomGen.binomial(n, p, size))
# prints
# [4 4 6 6 5 4 5 4 6 7]
# [4 8 6 3 5 7 6 4 6 4]
# This should be the case which we mostly want (DESIRABLE). If we are using both Numpy based and
#Scipy based random number generators/function, then not only do we have no repetition of
#random number sequences but also have reproducibility of results in this case.
