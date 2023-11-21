
<div align="center">

![](./docs/images/logo_small_small.png)

[![GitHub release](https://img.shields.io/github/release/gbene/FracAbility?&sort=semver&color=orange)](https://github.com/gbene/FracAbility/releases/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-orange)](#license)
[![issues - FracAbility](https://img.shields.io/github/issues/gbene/FracAbility)](https://github.com/gbene/FracAbility/issues)
[![Made with Python](https://img.shields.io/badge/Python->=3.8-orange?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
![maintained - yes](https://img.shields.io/badge/maintained-yes-green)
</div>

**FracAbility** is a Python toolbox that can be used to analyse fracture networks in digitalized rock
outcrops. This package provides tools to:

1. Define the topology of fracture networks 
2. Statistically analyze fracture length distributions while taking into consideration 
right censoring effects ([survival analysis](https://en.wikipedia.org/wiki/Survival_analysis)). 

The name Frac**Ability** recalls the [reliability](https://github.com/MatthewReid854/reliability/tree/master)<sup>1</sup> 
library that inspired and helped in the creation of this project. 


## Quick introduction ⚡

Fracture networks are essential for the analysis and modelling of mechanical and hydraulic properties 
of rock masses. Recently, the use of Digital Outcrop Models (**DOMs**) provided a solid framework for the collection 
of large and quantitative datasets from which different properties can be extracted.
Because of the complex nature of exposed rock outcrops, statistical model fitting can sometimes be challenging. 
Areas covered by rock debree, vegetation patches or simply the outer boundaries of the outcrop can 
introduce right-censoring bias and can often lead to parameter underestimation.

The following diagram represents an idealized rock outcrop. We can define the wider rectangle as the entire 
fractured object while the smaller one as the outcrop that we can see and measure. We can immediately 
see what is going wrong; many of the fractures that we can measure are incomplete thus leading to underestimate 
fracture length. 

![](./docs/images/example_diagram.png)

Tools are needed to correct for this bias. Survival analysis techniques, although usually applied  
in function of time and not space, accomplishes exactly this.

## Features 📋

- **Shapefile importing support**


- **Rapid topology analysis and identification of I,Y,X and U nodes**


- **Backbone(s) identification**


- **Statistical analysis tools:**
    + Empirical CDF and SF calculation
    + Distribution fitting
    + Statistical model testing


- **Plotting tools:**
    + Network objects plotting using matplotlib or vtk
    + Ternary node plot 
    + Rose diagram
    + Statistical plotting

## Installation 🔧

To install fracability pip can be used:

```bash
pip install fracability
```

## Documentation

For usage details please refer to the documentation:

[![View - Online docs](https://img.shields.io/badge/View-Online_docs-blue?style=for-the-badge)](https://fracability.readthedocs.io/en/latest/index.html "Go to online documentation")

[![view - Documentation](https://img.shields.io/badge/view-Documentation-blue?style=for-the-badge)](/docs/ "Go to project documentation")



## References 🎓

1. Reid, M. (2020). MatthewReid854/reliability: v0. 5.1. version v0, 5.


## License

Released under [AGPL-3.0](/LICENSE) by [@gbene](https://github.com/gbene)
