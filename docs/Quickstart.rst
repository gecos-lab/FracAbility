.. image:: images/logo.png

-------------------------------------

Quickstart for FracAbility
=========================================================


If you are new to using Python, you will first need to install a `Python 3 <https://www.python.org/downloads/>`_ interpreter and also install an IDE so that you can interact with the code. There are many `good IDEs <https://www.guru99.com/python-ide-code-editor.html>`_ available including `Pycharm <https://www.jetbrains.com/pycharm/>`_, `Spyder <https://www.spyder-ide.org/>`_ and `Jupyter <https://jupyter.org/install.html>`_.

We also advise to use a virtual environment manager such as `Anaconda  <https://www.anaconda.com/download/success>`_. If you are new to virtual environment creation the following chapter will describe how to create one. If you already know or don't want to install FracAbility in an environment, skip the following chapter.

Prepping environment with anaconda
++++++++++++++++++++++++++++++++++

After you installed Anaconda, open the command prompt (type in the searchbar "conda prompt" if you are on Windows) and type the following:

.. code-block:: console

    conda create -n Fracability python=3.10


After the environment is created activate it

.. code-block:: console

    conda activate Fracability


Done!

Installation and upgrading
----------------------------

To install fracabilty you can use pip

.. code-block:: console

    python -m pip install fracability

If you want to install it along with jupyter (to run the examples in the Tutorial section)
you can also do:

.. code-block:: console

    python -m pip install fracability[jupyter]

To upgrade a previous installation of *fracability* to the most recent version, open your command prompt and type:

.. code-block:: console

    python -m pip install --upgrade fracability

Done!