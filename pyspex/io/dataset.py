#!/usr/bin/env python

# =========================================================
"""
  Python module to read and write SPEX res and spo files.
  See this page for the format specification: 
      
    http://var.sron.nl/SPEX-doc/manualv3.04/manualse108.html#x122-2840008.2
  
  This module contains the data class:
 
    DATA:      Contains the collection of spectra and
               responses organized in SPEX regions   
 
  Dependencies:
    - numpy:      Array operations
    - spo:        The spo class from this pyspex data module
    - res:        The res class from this pyspex data module
"""
# =========================================================

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import numpy as np

from .region import Region
from .spo import Spo
from .res import Res

standard_library.install_aliases()


# =========================================================
# Data class
# =========================================================

class Dataset:
    """The dataset class is the most general class containing a 
       dataset with multiple regions. Using this class, users
       can read, write and manipulate spectral datasets."""

    def __init__(self):
        self.regions = []  #: List of regions

    # -----------------------------------------------------
    # Read one region from a spo and res file.
    # -----------------------------------------------------

    def read_region(self, iregion, spofile, resfile, label=""):
        """Read one region with number iregion from the two SPEX files and add it to the dataset."""

        # Read the spo and res files in a temporary object
        tspo = Spo()
        tspo.read_file(spofile)

        tres = Res()
        tres.read_file(resfile)

        # Create new region
        reg = Region()

        # Return desired region and save into local region object
        reg.spo = tspo.return_region(iregion)
        reg.res = tres.return_region(iregion)

        # Adapt region number to local set
        reg.res.region = reg.res.region + len(self.regions)

        # Run consistency checks
        reg.check()

        # Add label to the region
        self.label = label

        # Add region to list of regions
        self.regions.append(reg)

    # -----------------------------------------------------
    # Read all the regions from a spo and res file.
    # -----------------------------------------------------

    def read_all_regions(self, spofile, resfile):
        """Read all the regions from a spo and res file and add them to the dataset."""

        # Read the spo and res files in a temporary object
        tspo = Spo()
        tspo.read_file(spofile)

        tres = Res()
        tres.read_file(resfile)

        # Check if the number of regions in both files are the same
        if tspo.nregion != tres.nregion:
            print("Error: the spo and res files do not have the same number of regions!")
            return

        for i in np.arange(tspo.nregion):
            # Initialize a new region
            reg = Region()

            reg.spo = tspo.return_region(i + 1)
            reg.res = tres.return_region(i + 1)

            reg.res.region = reg.res.region + len(self.regions)

            # Run consistency checks
            reg.check()

            # Add region to list of regions
            self.regions.append(reg)

    # -----------------------------------------------------
    # Write one region to a spo and res file.
    # -----------------------------------------------------

    def write_region(self, spofile, resfile, iregion, ext_rate=False, overwrite=False, history=None):
        """Write one region to a spo and res file."""

        if len(self.regions) >= iregion > 0:
            self.regions[iregion - 1].spo.write_file(spofile, ext_rate=ext_rate, overwrite=overwrite, history=history)
            self.regions[iregion - 1].res.write_file(resfile, overwrite=overwrite, history=history)
        else:
            print("Error: region number not found!")

    # -----------------------------------------------------
    # Write all the regions to a spo and res file.
    # -----------------------------------------------------

    def write_all_regions(self, spofile, resfile, ext_rate=False, overwrite=False, history=None):
        """Write all regions in the data object to spo and res. """
        tspo = Spo()
        tres = Res()

        i = 1
        for ireg in self.regions:
            tspo.add_spo_region(ireg.spo)
            tres.add_res_region(ireg.res, i)
            i = i + 1

        tspo.write_file(spofile, ext_rate=ext_rate, overwrite=overwrite, history=history)
        tres.write_file(resfile, overwrite=overwrite, history=history)

    # -----------------------------------------------------
    # Show a summary of the dataset, similar to data show in SPEX
    # -----------------------------------------------------

    def show(self):
        """Show a summary for the entire dataset"""
        for ireg in np.arange(len(self.regions)):
            print("===========================================================")
            print(" Part {0}".format(ireg))
            self.regions[ireg].show()
            print("")