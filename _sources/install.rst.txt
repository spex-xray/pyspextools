Install pyspex
==============

Download the pyspex source code from Github and, if necessary, extract it in a 
convenient directory.

Before you continue, please think about where you want to install pyspex. It 
may be wise to create an Anaconda environment where pyspex can be compiled 
with the most compatible versions of the modules that pyspex depends on.

Within a conda environment, install pyspex as follows::

  (conda) linux:~/pyspex> python setup.py install
  
If you do not have conda, install it in a local python module directory::

  linux:~/pyspex> python setup.py install --prefix=$HOME/python
  
Make sure that the '$HOME/python/lib/pythonx.x/site-packages' directory
is in the PYTHONPATH environment variable.    

