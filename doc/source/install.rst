Install pyspextools
===================

Before you install
------------------

From pyspextools version 0.5.0, you need a Python 3 environment to install pyspextools.
We recommend to install the pyspextools module in a virtual environment like mamba or conda
to manage the dependencies. Mamba is the open-source alternative to conda and works in a nearly
identical way. It uses conda-forge as package repository. To download and install mamba, please
visit the `Conda forge download page <https://conda-forge.org/download/>`_.

To do so, create your own mamba environment first.
In the example below, we create a mamba environment ``spex`` assuming you already have
installed mamba successfully.
The commands below create a new mamba environment and activate it in your shell (you can replace
``mamba`` with ``conda`` if you have anaconda installed)::

    linux:~> mamba create -n spex -c spexxray python=3.12 numpy astropy sphinx sphinx-argparse pyspextools
    linux:~> mamba activate spex
    (spex) linux:~>

To use pyspextools later, each time you open a terminal, you need to activate the mamba spex environment
using the ``mamba activate spex`` command.

Install pyspextools through Mamba in other environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyspextools can be installed directly in mamba. Of course, you can use the mamba
environment created in the previous step, but it should also work in other mamba or conda environments.

The command below installs pyspextools in your mamba environment::

    (spex) user@linux:~> mamba install -c spexxray pyspextools

It downloads pyspextools from the `spexxray channel at Anaconda <https://anaconda.org/spexxray>`_.

Non-conda environments
~~~~~~~~~~~~~~~~~~~~~~

It is also possible to install pyspextools natively on your operating system (Linux and Mac OS). To avoid dependency
issues, make sure you have installed the python modules that pyspextools depends on. On Linux, that can be done using
``apt-get install`` commands for Debian-like systems and ``yum install`` for RedHat-like systems. For Debian-like systems,
the following command should install all dependencies for python 3::

    linux:~> sudo apt-get install python3-future python3-numpy python3-astropy python3-sphinx-argparse

If you have installed ``pip``, then you can try to just run the ``pip install`` commands below and hope there are no
dependency conflicts.

Install using pip
-----------------

Pyspextools can be easily installed with pip using the following command (with or without conda/mamba environment)::

    (spex) linux:~> pip install pyspextools


Install from GitHub
~~~~~~~~~~~~~~~~~~~

Pyspextools can also be installed with pip using the Github git link to get the latest (bleeding edge) version::

    (spex) linux:~> pip install git+https://github.com/spex-xray/pyspextools.git


Install using python build
~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the pyspextools source code from Github and, if necessary, extract it in a convenient directory.

Before you continue, please think about where you want to install pyspextools. If you have a
dedicated conda environment, conda will take care of this. Otherwise, you need to specify a
suitable environment to install pyspextools in.

Within an environment, install pyspextools as follows::

  (spex) linux:~/pyspextools> python -m build && pip install dist/pyspextools-0.7.1.tar.gz


Dependency issues
-----------------

The install instructions above should take care of all the mandatory dependencies of the module. If not,
then please consider to create a fresh conda environment to install pyspextools in. If that does not help, create
an issue report on our `Github issues page <https://github.com/spex-xray/pyspextools/issues>`_ and describe the problem.

Notes on the pyspextools dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyspextools works Python 3. We try to keep the dependencies limited to ensure the stability of the module.
Currently, the dependencies are:

- numpy
- astropy

For the generation of documentation, the following packages are needed:

- sphinx (version >= 1.4)
- sphinx-argparse

For some of the examples, other packages are used, like pyatomdb, but they are not required for the pyspextools
module to function.
