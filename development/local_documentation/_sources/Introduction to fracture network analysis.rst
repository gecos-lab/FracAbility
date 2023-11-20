.. image:: images/logo.png

-------------------------------------

Introduction and scope of the FracAbility library.
=========================================================

Recently, the use of :term:`Digital Outcrop Models (DOMs)` provided a solid framework for the
collection of large and quantitative datasets from which different properties can be extracted. DOMs, and more in general
rock outcrops, can be viewed as natural sections of a given rock volume, in fact the big advantages of DOMs based analysis
lie on the possibility of extracting objective mesoscale information of the rock volume while having a strong field control.
On the flip side, outcrops need to be properly oriented both with the structures that we need to study and
between different outcrops.

The analysis of many optimal outcrops related to the same rock volume can extrapolate and relate different parameters
to constrain the volumes properties.

With FracAbility we focus on investigating the topology and length distribution parameters in 2D and 2.5D maps
of digitalized fracture networks obtained from DOMs. Because of the complex nature of exposed rock outcrops,
fitting parametric statistical models to data can sometimes be challenging.
Areas covered by rock debris, vegetation patches or simply the outer boundaries of the outcrop can
introduce right-censoring bias and can often lead to underestimation of the length parameter
(i.e. the intersection of a fracture surface with the outcrop surface).
Classically this issue is resolved by estimating the parameter using empirical formulas based on precise and
binding hypothesis. A more statistical and quantitative approach is needed to obtain such parameters and
:term:`survival analysis` techniques, typically used in disciplines such as biology or engineering, can be used to provide
such corrections.


In the following chapters we briefly introduce the concept of fracture networks, their structure and the different analysis
that can be carried out on them. We will focus also on introducing fracture network topological analysis and on fracture length distributions analysis
applying `survival analysis <https://en.wikipedia.org/wiki/Survival_analysis>`_ techniques for
right-censoring bias correction.

Theory index
----------------------

.. toctree::
  :maxdepth: 2
  :glob:

  Theory reference