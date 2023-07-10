# FracAbility: A python toolbox for survival analysis in fractured rock systems
**Gabriele Benedetti**$^1$, Stefano Casiraghi$^1$, Andrea Bistacchi$^1$

$^1$ Università degli Studi di Milano-Bicocca, Dipartimento di Scienze dell’Ambiente e della Terra, Milano, Italy


Fracture networks are essential for the analysis and modelling of mechanical and hydraulic properties of rock masses. Applications such as research or exploitation of water, natural gas and petroleum reservoirs, all rely heavily in creating fracture models to understand the spatial distribution of fractures and their properties in 3D space. Recently, the use of Digital Outcrop Models (DOMs) overcame the limitations of the classic field survey providing a solid framework for the collection of large and quantitative datasets from which different properties can be extracted. 

Of particular interest are the topology and length distribution, but for the latter, the intrinsic complex nature of exposed rock pavement can introduce bias in the parameters estimation. Areas covered by rock debree, vegetation or simply the outcrops' outer boundaries can lead to censoring of fractures traces, causing an underestimation of the mean and variance of the population. We propose FracAbility, a new python toolbox that provides methods for investigating fracture lengths by applying survival analysis techniques, recently implemented in the latest version of scipy, typically used in biological research and industrial profiling (known as reliability analysis). Although the real lengths of the censored objects will never be known, when fitting a distribution it is possible to apply these statistical tools and consider censored data thus correcting the bias in the parameters estimation. 


