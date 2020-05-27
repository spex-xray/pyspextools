Install pyspextools
===================

Before you install
------------------

We recommend to install the pyspextools module in a virtual environment like conda to manage the dependencies.
To do so, create your own conda environment first (See this
`tutorial <https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/>`_).
In the example below, we create the conda environment `spex` assuming you already have installed conda successfully.
The commands below create a new conda environment and activate it in your shell::

    linux:~> conda create -n spex python=3.6 numpy astropy future
    linux:~> conda activate spex
    (spex) linux:~>

To use pyspextools later, each time you open a terminal, you need to activate the conda spex environment
using the `conda activate spex` command.

Non-conda environments
~~~~~~~~~~~~~~~~~~~~~~

It is also possible to install pyspextools natively on your operating system (Linux and Mac OS). To avoid dependency
issues, make sure you have installed the python modules that pyspextools depends on. On Linux, that can be done using
`apt-get install` commands for Debian-like systems and `yum install` for RedHat-like systems. For Debian-like systems,
the following command should install all dependencies for python 3::

    linux:~> sudo apt-get install python3-future python3-numpy python3-astropy python3-sphinx-argparse

If you have installed `pip`, then you can try to just run the `pip install` commands below and hope there are no
dependency conflicts.

Install
-------

Pyspextools can be easily installed with pip using the following command (with or without conda environment)::

    (spex) linux:~> pip install pyspextools


Install from GitHub
~~~~~~~~~~~~~~~~~~~

Pyspextools can also be installed with pip using the Github git link to get the latest (bleeding edge) version::

    (spex) linux:~> pip install git+https://github.com/spex-xray/pyspextools.git


Install using setup.py
~~~~~~~~~~~~~~~~~~~~~~

Download the pyspextools source code from Github and, if necessary, extract it in a convenient directory.

Before you continue, please think about where you want to install pyspextools. If you have a
dedicated conda environment, conda will take care of this. Otherwise, you need to specify a
suitable directory to install pyspextools in.

Within a conda environment, install pyspextools as follows::

  (spex) linux:~/pyspextools> python setup.py install

If you do not have conda, install it in a local python module directory::

  linux:~/pyspextools> python setup.py install --prefix=$HOME/python

In that case, make sure that the '$HOME/python/lib/pythonx.x/site-packages' directory
is mentioned in the PYTHONPATH environment variable.

Dependency issues
-----------------

The install instructions above should take care of all the mandatory dependencies of the module. If not,
then please consider to create a fresh conda environment to install pyspextools in. If that does not help, create
an issue report on our `Github issues page <https://github.com/spex-xray/pyspextools/issues>`_ and describe the problem.

Notes on the pyspextools dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyspextools works both in Python 2.7 and Python 3, thanks to the backports from the 'future' module. We try to keep
the dependencies limited to ensure the stability of the module. Currently, the dependencies are:

- numpy
- astropy
- future (provides backward compatibility with Python 2.7)

For the generation of documentation, the following packages are needed:

- sphinx (version >= 1.4)
- sphinx-argparse

For some of the examples, other packages are used, like pyatomdb, but they are not required for the pyspextools
module to function.
