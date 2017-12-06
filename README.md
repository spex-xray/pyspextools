# PySPEX

PySPEX is a collection of python tools for the SPEX X-ray spectral fitting package (see the [SPEX website](http://www.sron.nl/spex)). 

[Full documentation of PySPEX](https://spex-xray.github.io/pyspex/)

## Install

To install PySPEX, download or check-out the source code from this page. 
Before you continue, please think about where you want to install pyspex.
It may be wise to create an Anaconda environment where pyspex can be compiled with the most compatible versions of the modules that pyspex depends on.

Within a conda environment, install pyspex as follows:
```
(conda) linux:~/pyspex> python setup.py install
```
If you do not have conda, install it in a local python module directory:
```
linux:~/pyspex> python setup.py install --prefix=$HOME/python
```
Make sure that the `$HOME/python/lib/pythonx.x/site-packages` directory is in the PYTHONPATH environment variable.

## Usage

Currently, there is one class available in PySPEX to help users create their own
model in SPEX. This class is `pyspex.user.IO` and handles the communication between SPEX and the user defined model. 

### SPEX user model examples

See the `examples` directory for examples of user models. The most basic model is myusermodel.py. This program can be modified to the user needs.
