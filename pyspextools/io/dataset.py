#!/usr/bin/env python

# =========================================================
"""
  Python module to read and write SPEX res and spo files.
  See this page for the format specification: 
      
    https://spex-xray.github.io/spex-help/theory/response.html
  
  This module contains the data class:
 
    DATA:      Contains the collection of spectra and
               responses organized in SPEX regions   
 
  Dependencies:
    - numpy:      Array operations
    - spo:        The spo class from this pyspextools data module
    - res:        The res class from this pyspextools data module
"""
# =========================================================

import numpy as np
import pyspextools.messages as message

from .region import Region
from .spo import Spo
from .res import Res


# =========================================================
# Data class
# =========================================================

class Dataset:
    """The dataset class is the most general class containing a 
    dataset with multiple regions. Using this class, users
    can read, write and manipulate spectral datasets.

    :ivar regions: List of regions.
    :vartype regions: list
    :ivar config: Response configuration (combinations of sector and region values).
    :vartype config: numpy.ndarray
    """

    def __init__(self):
        """Initialise a SPEX dataset."""
        self.regions = []
        self.config = np.empty(shape=[0, 2], dtype=int)

    # -----------------------------------------------------
    # Read one region from a spo and res file.
    # -----------------------------------------------------

    def read_region(self, isector, iregion, spofile, resfile, label=""):
        """Read one region with number iregion from the two SPEX files and add it to the dataset.

        :param isector: Sector number associated with the region to select.
        :type isector: int
        :param iregion: Region number to select.
        :type iregion: int
        :param spofile: File name of the .spo file.
        :type spofile: str
        :param resfile: File name of the .res file.
        :type resfile: str
        :param label: Text string to identify the region (optional).
        :type label: str
        """

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

        # Add the sector and region to the config variable of this dataset
        self.config = np.append(self.config, [[isector, iregion]], axis=0)

    # -----------------------------------------------------
    # Read all the regions from a spo and res file.
    # -----------------------------------------------------

    def read_all_regions(self, spofile, resfile):
        """Read all the regions from a spo and res file and add them to the dataset.

        :param spofile: File name of the input .spo file.
        :type spofile: str
        :param resfile: File name of the input .res file.
        :type resfile: str
        """

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
        config = self.read_config(tres)

        # Update the response configuration
        if self.config.size == 0:
            self.config = config
            regmax = 0
            secmax = 0
        else:
            secmax, regmax = np.amax(self.config, axis=0)

        for i in np.arange(tspo.nregion):
            # Initialize a new region
            reg = Region()

            reg.spo = tspo.return_region(config[i, 1])
            reg.res = tres.return_region(config[i, 0], config[i, 1])

            # Run consistency checks
            reg.check()

            # Add region to list of regions
            self.regions.append(reg)

            reg.increase_region(regmax)

        self.update_config()

    # -----------------------------------------------------
    # Append a region object to the dataset
    # -----------------------------------------------------
    def append_region(self, region, isector, iregion):
        """Append a region object to the dataset.

        :param region: Input region object.
        :type region: pyspextools.io.Region
        :param isector: Sector number to be selected from the region object.
        :type isector: int
        :param iregion: Region number to be selected from the region object.
        :type iregion: int
        """

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

    def write_region(self, spofile, resfile, iregion, exp_rate=True, overwrite=False, history=None):
        """Write one region to a spo and res file.

        :param spofile: File name of the input .spo file.
        :type spofile: str
        :param resfile: File name of the input .res file.
        :type resfile: str
        :param iregion: Region number to be selected from the region object.
        :type iregion: int
        :param exp_rate: Write an EXP_RATE column or not.
        :type exp_rate: bool
        :param overwrite: Should we overwrite existing files?
        :type overwrite: bool
        :param history: History information.
        :type history: List/Array of strings
        """

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

    def write_all_regions(self, spofile, resfile, exp_rate=True, overwrite=False, history=None):
        """Write all regions in the data object to spo and res.

        :param spofile: File name of the input .spo file.
        :type spofile: str
        :param resfile: File name of the input .res file.
        :type resfile: str
        :param exp_rate: Write an EXP_RATE column or not.
        :type exp_rate: bool
        :param overwrite: Should we overwrite existing files?
        :type overwrite: bool
        :param history: History information.
        :type history: List/Array of strings
        """
        tspo = Spo()
        tres = Res()

        i = 0
        for ireg in self.regions:
            tspo.add_spo_region(ireg.spo)
            tres.add_res_region(ireg.res, isector=self.config[i, 0], iregion=self.config[i, 1])
            i = i + 1

        stat = tspo.write_file(spofile, exp_rate=exp_rate, overwrite=overwrite, history=history)
        if stat != 0:
            message.error("Writing SPO file failed.")
            return 1

        stat = tres.write_file(resfile, overwrite=overwrite, history=history)
        if stat != 0:
            message.error("Writing RES file failed.")
            return 1

        return 0

    # -----------------------------------------------------
    # Function to read the response configuration
    # -----------------------------------------------------

    def read_config(self, res):
        """Read the response configuration.

        :param res: SPEX response object.
        :type res: pyspextools.io.Res
        """
        config = np.empty(shape=[0, 2], dtype=int)
        psector = 0
        pregion = 0
        for i in np.arange(res.ncomp):
            # Loop through components to find sector-region combinations
            if (res.region[i] != pregion) or (res.sector[i] != psector):
                config = np.append(config, [[res.sector[i], res.region[i]]], axis=0)
                psector = res.sector[i]
                pregion = res.region[i]

        return config

    # -----------------------------------------------------
    # Function to update the response configuration
    # -----------------------------------------------------

    def update_config(self):
        """Update the response configuration."""
        self.config = np.empty(shape=[0, 2], dtype=int)
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
    # Function to assign a new sector number to a region
    # -----------------------------------------------------

    def assign_sector(self, iregion, newsector):
        """Assign a new sector number to a specific region.

        :param iregion: Region number to assign new sector number for.
        :type iregion: int
        :param newsector: New sector number.
        :type newsector: int
        """
        if len(self.regions) >= iregion > 0:
            self.regions[iregion-1].set_sector(newsector)
            self.update_config()
        else:
            print("Error: region number not found!")
            return 1

    # -----------------------------------------------------
    # Function to assign a new region number to a region
    # -----------------------------------------------------

    def assign_region(self, iregion, newregion):
        """Assign a new region number to a specific region.

        :param iregion: Region number to assign new number for.
        :type iregion: int
        :param newregion: New region number.
        :type newregion: int
        """
        if len(self.regions) >= iregion > 0:
            self.regions[iregion-1].set_region(newregion)
            self.update_config()
        else:
            print("Error: region number not found!")
            return 1

    # -----------------------------------------------------
    # Function to assign a new region number to a region
    # -----------------------------------------------------

    def assign_sector_region(self, iregion, newsector, newregion):
        """Assign a new sector and region number to a specific region.

        :param iregion: Region number to assign new sector number for.
        :type iregion: int
        :param newsector: New sector number.
        :type newsector: int
        :param newregion: New region number.
        :type newregion: int
        """
        if len(self.regions) >= iregion > 0:
            self.regions[iregion-1].set_sector(newsector)
            self.regions[iregion-1].set_region(newregion)
            self.update_config()
        else:
            print("Error: region number not found!")
            return 1

    # -----------------------------------------------------
    # Show a summary of the dataset, similar to data show in SPEX
    # -----------------------------------------------------

    def show(self):
        """Show a summary for the entire dataset"""
        for ireg in np.arange(len(self.regions)):
            print("===========================================================")
            print(" Part {0}".format(ireg+1))
            self.regions[ireg].show(isector=self.config[ireg, 0], iregion=self.config[ireg, 1])
            print("")
