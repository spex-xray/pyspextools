.. _datamodule:

pyspex.io: The SPEX data format
===============================

This is a Python class to read, write and manipulate 
SPEX spectrum and response file (.spo and .res). The
format of these FITS files is described in Chapter 5
of the SPEX manual: http://var.sron.nl/SPEX-doc/ 

.. automodule:: pyspex.io

Reading and writing datasets
----------------------------

SPEX res and spo files can contain a set of spectra and responses from, for example,
different instruments used in the same observation or spectra from different spatial 
regions. Each combination of a spectrum and response is called a region in SPEX
(see the region class below). The dataset class is basically a list of regions and 
allows the user to add and remove regions from a dataset.  

   .. autoclass:: pyspex.io.Dataset
      :members:

The region class
----------------

A combination of a spectrum and its response matrix is called a region in SPEX. This
name originates from the idea that a dataset (see above) can contain spectra extracted 
from multiple regions in a spatial image. The region class combines a spo and res 
object into one region and provides tests to see if the spo and res files actually
belong to each other. 

   .. autoclass:: pyspex.io.Region
      :members:

The spo class
-------------

The SPEX .spo file contains the source and background spectra, including information
about systematic uncertainties and grouping. This class manages the reading and writing
of (regions) in spo files.

   .. autoclass:: pyspex.io.Spo
      :members:

The res class
-------------

The SPEX .res file contains the response matrix and effective area information for a 
spectrum. This class manages the reading and writing of (regions) in res files.

   .. autoclass:: pyspex.io.Res
      :members:
