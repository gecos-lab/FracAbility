# FracAbility: A python toolbox for survival analysis in fractured rock systems
**Gabriele Benedetti** $^1$, Stefano Casiraghi $^1$, Andrea Bistacchi $^1$

$^1$ _Università degli Studi di Milano-Bicocca, Dipartimento di Scienze dell’Ambiente e della Terra, Milano, Italy_


Fracture networks are essential for the analysis and modelling of mechanical and hydraulic properties of rock masses. Research or exploitation of water, natural gas and petroleum reservoirs, all heavily rely on creating fracture models to understand the distribution of fractures and their properties in 3D space. Recently, the use of Digital Outcrop Models (DOMs) provided a solid framework for the collection of large and quantitative datasets from which different properties can be extracted. Of particular interest are the topology and length distribution parameters, essential for building stochastic fracture networks. 

We propose FracAbility, a new python toolbox that enables the users to investigate both topology and fracture lengths in digitalized fracture networks. We provide tools to optimize fracture networks assuring water tight connections between fractures, methods to calculate and classify the node topology of the network, and fit statistical distributions to the length data.

Because of the complex nature of exposed rock outcrops, statistical model fitting can sometimes be challenging. Areas covered by rock debree, vegetation patches or simply the outer boundaries of the outcrop can introduce right-censoring bias and can often lead to parameter underestimation. Particular attention has been given to this issue by applying survival analysis techniques, typically used in other disciplines such as in biology or engineering. These specific statistical tools, recently implemented in the last scipy package release, can be used to manage right-censored datasets, and thus correctly and efficiently fit a distribution to the data. In FracAbility, it is possible to fit multiple distributions while considering for right-censoring bias and carry out statistical tests to rank the different models and determine which is the most “fitting”.

The modular nature of this library brings different advantages. Most importantly, being a stand-alone package, FracAbility can be used in different independent applications, scripts, jupyter notebooks or directly in software with python backends or APIs such as QGIS or ArcGIS.
