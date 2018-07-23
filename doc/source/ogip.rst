
pyspex.io.ogip: Importing OGIP files
====================================

The pyspex module offers to import OGIP spectral files and convert them to 
SPEX format. The OGIP interface is provided by the HEASP module from NASA's 
HEASOFT package (Keith Arnaud, `HEASP <https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/headas/heasp/>`_).

.. NOTE::
   This functionality depends on the HEASP module, which currently
   only supports Python 2.7!
 
The pyspex OGIPRegion class contains methods to read a source spectrum, background 
spectrum, response file and effective area file, and save them as a SPEX region, which 
can be used by the other methods in the pyspex module. Please note that the
module does a direct translation of the OGIP files. No filtering of bad channels or
other optimizations are performed. Bad channel filtering and optimizations can be
found in pyspex.data.

The main method of the OGIPRegion class is read_region. We recommend to use this 
method to read a combination of a spectrum and response matrix. This method will
do the necessary checks to make sure that the final region object is consistent.
Since this class depends on the HEASP module, this class is not imported 
automatically, but needs to imported separately, for example::
 
    import pyspex.io.ogip as ogip
    oregion = ogip.OGIPRegion()

The oregion instance above will be an extended version of the parent region class of
pyspex and will have the same functionality.  

Notes about converting PHA to SPEX format
-----------------------------------------

The methods in this class perform an almost direct copy of the PHA spectrum files into 
SPEX format. The conversion of source and background spectra into (background subtracted) 
source and background rates with errors is relatively straightforward. The areascal and
backscal values from the PHA file are used to scale the spectral rates and errors as they
are stored in SPEX format.

.. NOTE::
   The method of subtracting the background from a spectrum provides wrong
   results in case of Poisson distributed data and C-statistics. It would be better to
   use a model for the background instead. Such alternatives will be implemented from
   SPEX version >=3.05.00.

This method does not yet ignore bad channels. In pyspex this is regarded as additional 
filtering of the data and is implemented in a different method (ref). Therefore, this
method alone could give different results from the SPEX trafo program.
 

Notes about converting RMF to SPEX format
-----------------------------------------

While the conversion of PHA format spectra to SPEX format is relatively trivial, the 
conversion of response matrices is more interesting. The RMF format chooses to store
response groups, which describe a particular redistribution function, per model energy 
bin. Since there can be multiple physical effects causing their own characteristic 
response function, there can be multiple groups associated with a particular model energy, 
each describing the redistribution function for a particular physical effect. 

In SPEX, the groups are not organised per model energy bin, but per physical effect, which 
is called a response component. This allows more freedom in the binning that is needed for 
the group and thus the storage space required. The optimal range and binning needed for a sharp 
Gaussian response feature is obviously different from a broad-band power-law redistribution 
function. The latter can be binned in a much coarser way than the Gaussian case. 

However, the RMF files do not contain information about the physical response components. 
There are methods to detect similar groups in an RMF file and organise them in a component,
but we did not add this method to this class. This class does a direct copy of all the groups 
of the RMF to one SPEX response component. If a more optimal re-arrangement of groups in 
components is desired, that should be done with other methods in the pyspex module (ref). 


The OGIP class description
--------------------------

.. autoclass:: pyspex.io.ogip.OGIPRegion
   :members:
