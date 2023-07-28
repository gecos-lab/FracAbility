.. image:: images/logo.png

-------------------------------------

Introduction to fracture network analysis
=========================================================

In this page we briefly introduce the concept of fracture networks, their composition and the analysis
that can be carried out on them. We also focus on of fracture length distributions analysis and the
application of `survival analysis <https://en.wikipedia.org/wiki/Survival_analysis>`_ techniques for
right-censoring bias correction.


Fracture networks
---------------------------------

Fracture networks have an essential control on the hydraulic properties of rock masses. Research or exploitation
of water, hydrothermal fluids, natural gas, and the characterization of reservoirs for carbon sequestration and
hydrogen storage, all heavily rely on creating fracture models to understand the distribution of fractures and
their properties in 3D space. This is achieved by creating Discrete Fracture Network (DFNs) based on **stochastic**
algorithms. There are different DFN approaches provided by software:

+ `Petrel <https://www.software.slb.com/products/petrel>`_
+ `Move <https://www.petex.com/products/move-suite/>`_
+ `FracMan <https://www.golder.com/fracman/>`_
+ `DFNWorks <https://dfnworks.lanl.gov>`_.

All of these use many different parameters to drive the building of the model. The most important are summarized
in the following table:

.. figure:: images/mystic_table.png
   :align: center

   Summary table of the most important parameters used as input for DFNs. The distinction fracture network and fracture
   set identifies from where the property can be extracted.

Recently, the use of Digital Outcrop Models (DOMs) provided a solid framework for the
collection of large and quantitative datasets from which different properties can be extracted.
With FracAbility we focus on investigating the topology and length distribution parameters in 2D and 2.5D maps
of digitalized fracture networks.


Because of the complex nature of exposed rock outcrops, fitting parametric statistical models to data can sometimes
be challenging.
Areas covered by rock debris, vegetation patches or simply the outer boundaries of the outcrop can
introduce right-censoring bias and can often lead to underestimation of the length parameter
(i.e. the intersection of a fracture surface with the outcrop surface).

Classically this issue is resolved by estimating the parameter using empirical formulas based on precise and
binding hypothesis. A more statistical and quantitative approach is needed to obtain such parameters and
survival analysis techniques, typically used in disciplines such as biology or engineering, can be used to provide
such corrections.




Structure of a fracture network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fracture networks can be subdivided in three main different components:

1. Nodes
2. **Fractures**
3. Boundaries

.. figure:: images/frac_net.png
   :align: center

   Subdivision of a simple fracture network


**Fractures**

The most important of the three are unsurprisingly the fractures. This component can be further divided into **fracture
sets** (i.e. fractures that have the same genetic origin and processes). From analysing the fractures both on the
single fracture set or on the whole fracture network, we can derive all of the parameters described in the table.


**Nodes**

The nodes can be defined as the intersection points between two fractures (pertaining in the same or different set) and
are necessary to define the **topology** of the fracture network (i.e. how fractures usually terminate in the given outcrop).
Moreover the topology also helps in defining the connectivity of the fracture network.

**Boundaries**

Finally the boundaries are defined as the observational limits that the interpreter imposes in the outcrop. These can
delimit the areas of exposed rock where fractures can be measured or can define zones in which
interpretation cannot be carried out. The definition of these "interpretation voids" are extremely important both for
a correct estimation of the length parameter but also further on the pipline for the estimation of fracture density and
intensity; without them the overestimation of these parameters is typically assured.


Graph theory and node classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With graph theory we model how different objects relate to each other. In a fracture network, fractures are connected
in different ways (and sometimes even isolated). By applying this abstraction it is possible to extrapolate interesting
descriptive features by analysing the **relationships** between fractures and ignoring how they are positioned in
the geometric space.
A complex fracture network can be simplified by defining a Graph (G) composed of Edges (E) and Vertices (V) such that for each edge
there are two vertices. This means that the **degree** at each node (i.e. how many edges are connected to a node) enables
the classification of each node thus obtaining the relationships between fractures.

.. figure:: images/rel2graph.png
   :align: center

   Abstraction example of a small fracture network. Spatial relationships are partially conserved to help in the comparison.
   Higher abstraction is possible in which the spatial dimension is completely disregarded.

Node classes
+++++++++++++

Four classes of nodes have been defined:

+ I nodes: Given by a termination of a fracture in the outcrop
+ Y or T nodes: Given by a termination of a fracture on **another fracture**
+ X nodes: Given by crossing fractures
+ U nodes: Given by a termination of a fracture on a **boundary**

.. figure:: images/node_types.png
   :align: center

   Schematic representation of the different node classes. For each cell highlighted the corresponding node.


Geologically each node type can give information on the nature of the fracture and the genetic processes of the network.
I and U nodes define the "completeness" of the given fracture.
An isolated fracture (i.e. bounded by two I vertices) is whole and so its length is complete
while the presence of U nodes will identify a cut fracture with a partial length.

Y and X nodes are useful on the other hand to define the relative chronology. For example in fractures or joints, Y nodes identify
abutting relationships (i.e. older cutting younger). X nodes on the other hand indicate cross-cutting relationships.

I Y and X nodes also are useful to describe the connectivity of the network; connected networks will have a higher
proportions of Y and X nodes while the opposite will be defined by a dominance of I nodes graphically
represented by a ternary plot.

.. figure:: images/ternary_plot.png
   :align: center

   Ternary plot of a fracture network. The red dot corresponds to the I, Y and X nodes proportions of the outcrop. The
   contour lines are the average number of connections per fracture derived from equation **A6** in Manzocchi (2002).



Statistical parametrization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For DFNs it is essential to provide a length distribution model. This is used in model construction to guide the creation
of synthetic fractures with lengths that follow the given distribution. The immediate problem that arises is that
often fractures are cut by boundaries thus giving partial length information. This type of data is defined as **censored
data**.

Censoring
++++++++++
Survival (or reliability) analysis are rooted in the medical, biological and engineering sphere, thus the continuous
measured variable is **time**. In our case the measured variable is **space** (length) but the principles of survival
analysis are maintained since it is still a continuous variable censored by an observational limit. We can thus translate
the theory and definitions from a function of time to function of space.

In general censoring can be of three main types:

1. Right censoring: the fracture starts inside the boundary but terminates outside of it
2. Left censoring: The fractures starts and terminates outside the boundary
3. Interval censoring: The fracture is cut by internal holes (interpretational voids).

When trying to estimate a parameter from the data, and eventually fit a distribution, censored data must be corrected or
underestimation is assured.

In this
case the data is right-censored thus we can apply survival analysis techniques to correct for such bias. A in depth explanation
is provided in the `reliability page



Length parameter
+++++++++++++++++

By following the schematic below we can introduce the problem

.. image:: images/example_diagram.png
   :align: center