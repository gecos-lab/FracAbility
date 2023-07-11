# FracAbility: A python toolbox for survival analysis in fractured rock systems
**Gabriele Benedetti**$^1$, Stefano Casiraghi$^1$, Andrea Bistacchi$^1$

$^1$ Università degli Studi di Milano-Bicocca, Dipartimento di Scienze dell’Ambiente e della Terra, Milano, Italy


Fracture networks are essential for the analysis and modelling of mechanical and hydraulic properties of rock masses. Research or exploitation of water, natural gas and petroleum reservoirs, all rely heavily on creating fracture models to understand the spatial distribution of fractures and their properties in 3D space. Recently, the use of Digital Outcrop Models (DOMs) provided a solid framework for the collection of large and quantitative datasets from which different properties can be extracted. Of particular interest are the topology and length distribution parameters, essential in building stochastic fracture network. 
Because of the complex nature of exposed rock outcrops, the fitting of a distribution to the length data can be challenging and can lead to right-censoring. Areas covered by rock debree, vegetation or simply the outcrops' outer boundaries can introduce bias by interrupting traces thus leading in a wrong estimation of the mean and variance of the population.

We propose FracAbility, a new python toolbox that provides methods for investigating both topology and fracture lengths in digitalized fracture networks, with a specific focus on the correction of the latter for right-censoring bias. We use survival analysis techniques, recently implemented in the scipy package, to efficiently fit a distribution and consider censored data, thus correcting for the right-censoring bias. 

The modular nature of this library can bring different advantages. First, it is possible to rapidly analyse datasets structured in different ways. Second, being a stand-alone package, FracAbility can be used in different applications such as scripts, jupyter notebooks or directly in software with python backends or APIs such as QGIS or ArcGIS.
