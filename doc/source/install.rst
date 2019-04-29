Install pyspextools
===================

Install using pip and GitHub
----------------------------

Pyspex can be easily installed with pip using the Github git link::

    (myconda) linux:~> pip install git+https://github.com/spex-xray/pyspextools.git

We recommend to install the pyspex module in a virtual environment like conda, so create your
own conda environment (for example, myconda) first

Install using setup.py
----------------------

Download the pyspextools source code from Github and, if necessary, extract it in a
convenient directory.

Before you continue, please think about where you want to install pyspextools. It
may be wise to create an Anaconda environment where pyspextools can be compiled
with the most compatible versions of the modules that pyspextools depends on.

Within a conda environment, install pyspextools as follows::

  (conda) linux:~/pyspextools> python setup.py install

If you do not have conda, install it in a local python module directory::

  linux:~/pyspextools> python setup.py install --prefix=$HOME/python

Make sure that the '$HOME/python/lib/pythonx.x/site-packages' directory
is in the PYTHONPATH environment variable.

Dependencies
------------

The install instructions above should take care of all the mandatory dependencies of the module. Pyspextools works both in
Python 2.7 and Python 3, thanks to the backports from the 'future' module. We try to keep the dependencies limited to
ensure the stability of the module. Currently, the dependencies are:

- numpy
- astropy
- future (provides backward compatibility with Python 2.7)

For the generation of documentation, the following packages are needed:

- sphinx (version >= 1.4)
- sphinx-argparse

For some examples, other packages are used, like pyatomdb, but they are not required for the pyspex module to function.
