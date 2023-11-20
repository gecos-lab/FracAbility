.. image:: images/logo.png

-------------------------------------

Quickstart for FracAbility
=========================================================


Installation and upgrading
--------------------------

If you are new to using Python, you will first need to install a `Python 3 <https://www.python.org/downloads/>`_ interpreter and also install an IDE so that you can interact with the code. There are many `good IDEs <https://www.guru99.com/python-ide-code-editor.html>`_ available including `Pycharm <https://www.jetbrains.com/pycharm/>`_, `Spyder <https://www.spyder-ide.org/>`_ and `Jupyter <https://jupyter.org/install.html>`_.

Once you have Python installed, to install *fracability* for the first time, open your command prompt and type:

.. code-block:: console

    pip install fracability

To upgrade a previous installation of *reliability* to the most recent version, open your command prompt and type:

.. code-block:: console

    pip install --upgrade fracability


A quick example
---------------

A key feature of `fracability` is that Entities and functions are designed to be used in a modular way.
This allows flexibility for different workflows in which not all tools need to be used.

In this example, we will quickly illustrate a typical workflow to:

1. Create a FractureNetwork object and define its intersections
2. Visualize the data
3. Analyze the length statistics

Create a FractureNetwork entity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python


        import geopandas as gpd

        import pyvista as pv


        from fracability import Entities

        n_path = 'fracability/datasets/Fracture_network.shp'
        b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'

        frac_gpd = gpd.read_file(n_path)

        bound_gpd = gpd.read_file(b_path)


        fractures = Entities.Fractures(frac_gpd)

        boundaries = Entities.Boundary(bound_gpd)

        fracture_net = Entities.FractureNetwork()

        fracture_net.add_fractures(fractures)

        fracture_net.add_boundaries(boundaries)


These steps create a fracture network entity composed by the fractures and the interpretation boundaries. We now need to
identify the common nodes and define how many segments are connected to each node. This can be done using a couple of
specific functions

.. code:: python

        from fracability.geometric_operations import tidy_intersections
        from fracability.clean_operations import connect_dots
        from fracability.topology_operations import nodes_conn


        tidy_intersections(fracture_net) #tidy shapefile intersections
        connect_dots(fracture_net) #merge overlapping nodes
        nodes_conn(fracture_net) #calculate topological adjacency (number of segments per node)

In these few lines we:

1. Cleaned and tidied the intersections between fractures (F-F) and boundaries (F-B)
2. Defined common nodes
3. Calculated the number of segments connected to each node

Visualize the network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The fracture network entity can be visualized in different ways.

1. We can view the geopandas dataframe, functioning as the database.

2. We can plot the object in a 3D window using pyvista/vtk

3. We can plot the object in a 2D window using matplotlib

4. We can visualize the topological network (not recommended for big fracture networks).

.. code:: python

        print(fracture_net.fractures.entity_df)

        """

        """

        nodes = fracture_net.nodes.vtk_object

        nodes.set_active_scalars('class_id')

        plotter = pv.Plotter()

        plotter.add_mesh(fracture_net.vtk_object, color='white')
        plotter.add_mesh(nodes, render_points_as_spheres=True, point_size=10)
        plotter.view_xy()
        plotter.show()


Analyze length statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
