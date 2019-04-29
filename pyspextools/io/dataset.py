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
    - spo:        The spo class from this pyspextools data module
    - res:        The res class from this pyspextools data module
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
import pyspextools.messages as message

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
        self.config = np.empty(shape=[0,2], dtype=int)  #: Response configuration (combinations of sector and region values)

    # -----------------------------------------------------
    # Read one region from a spo and res file.
    # -----------------------------------------------------

    def read_region(self, isector, iregion, spofile, resfile, label=""):
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
        reg.res = tres.return_region(isector, iregion)

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

        # Read the response configuration
        self.read_config(tres)

        for i in np.arange(tspo.nregion):
            # Initialize a new region
            reg = Region()

            reg.spo = tspo.return_region(self.config[i,1])
            reg.res = tres.return_region(self.config[i,0],self.config[i,1])

            # Run consistency checks
            reg.check()

            # Add region to list of regions
            self.regions.append(reg)

    # -----------------------------------------------------
    # Append a region object to the dataset
    # -----------------------------------------------------
    def append_region(self, region, isector, iregion):
        """Append a region object to the dataset."""

        # Reset sector and region for incoming region
        for i in np.arange(len(region.res.region)):
            region.res.region[i] = iregion
            region.res.sector[i] = isector

        # Append the region
        self.regions.append(region)

        # Add the sector and region to the config variable of this dataset
        self.config = np.append(self.config, [[isector, iregion]], axis=0)

    # -----------------------------------------------------
    # Write one region to a spo and res file.
    # -----------------------------------------------------

    def write_region(self, spofile, resfile, iregion, exp_rate=False, overwrite=False, history=None):
        """Write one region to a spo and res file."""

        if len(self.regions) >= iregion > 0:
            self.regions[iregion - 1].spo.write_file(spofile, exp_rate=exp_rate, overwrite=overwrite, history=history)
            self.regions[iregion - 1].res.write_file(resfile, overwrite=overwrite, history=history)
        else:
            print("Error: region number not found!")
            return 1

        return 0

    # -----------------------------------------------------
    # Write all the regions to a spo and res file.
    # -----------------------------------------------------

    def write_all_regions(self, spofile, resfile, exp_rate=False, overwrite=False, history=None):
        """Write all regions in the data object to spo and res. """
        tspo = Spo()
        tres = Res()

        i = 0
        for ireg in self.regions:
            tspo.add_spo_region(ireg.spo)
            tres.add_res_region(ireg.res, isector=self.config[i,0], iregion=self.config[i,1])
            i = i + 1

        stat=tspo.write_file(spofile, exp_rate=exp_rate, overwrite=overwrite, history=history)
        if stat != 0:
            message.error("Writing SPO file failed.")
            return 1

        stat=tres.write_file(resfile, overwrite=overwrite, history=history)
        if stat != 0:
            message.error("Writing RES file failed.")
            return 1

        return 0

    # -----------------------------------------------------
    # Function to read the response configuration
    # -----------------------------------------------------

    def read_config(self,res):
        self.config = np.empty(shape=[0,2], dtype=int)
        pregion = 0   # Set previous region
        psector = 0   # Set previous sector
        for i in np.arange(res.ncomp):
            # Loop through components to find sector-region combinations
            if (res.region[i] != pregion) or (res.sector[i] != psector):
                self.config = np.append(self.config, [[res.sector[i], res.region[i]]], axis=0)
                pregion = res.region[i]
                psector = res.sector[i]

    # -----------------------------------------------------
    # Function to update the response configuration
    # -----------------------------------------------------

    def update_config(self):
        self.config = np.empty(shape=[0,2], dtype=int)
        pregion = 0   # Set previous region
        psector = 0   # Set previous sector
        for reg in self.regions:
            # Loop through components to find sector-region combinations
            if (reg.res.region[0] != pregion) or (reg.res.sector[0] != psector):
                self.config = np.append(self.config, [[reg.res.sector[0], reg.res.region[0]]], axis=0)
                pregion = reg.res.region[0]
                psector = reg.res.sector[0]
        else:
            message.error("Double sector and region identification.")

    # -----------------------------------------------------
    # Show a summary of the dataset, similar to data show in SPEX
    # -----------------------------------------------------

    def show(self):
        """Show a summary for the entire dataset"""
        for ireg in np.arange(len(self.regions)):
            print("===========================================================")
            print(" Part {0}".format(ireg+1))
            self.regions[ireg].show(isector=self.config[ireg,0],iregion=self.config[ireg,1])
            print("")
