#!/usr/bin/env python

# =========================================================
# Python module to read and write SPEX res and spo files.
# See this page for the format specification: 
#     
#   http://var.sron.nl/SPEX-doc/manualv3.04/manualse108.html#x122-2840008.2
# 
# This module contains the data class:
#
#   DATA:      Contains the collection of spectra and
#              responses organized in SPEX regions   
#
# Dependencies:
#   - numpy:      Array operations
#   - spo:        The spo class from this pyspex data module
#   - res:        The res class from this pyspex data module
# =========================================================

import numpy as np

from .spo import spo
from .res import res  

# See if Heasoft python modules are available
try:
    import heasp 
except ImportError:
    has_heasp = False
else:
    has_heasp = True

    
# =========================================================
# Region class
# =========================================================

class region:
    """A SPEX region is a spectrum/response combination for a
       specific observation, instrument or region on the sky.
       It combines the spectrum and response file in one object."""
    
    def __init__(self):
        self.spo=spo()
        self.res=res()

    def Check(self):
        """Check whether spectrum and response are compatible
           and whether the arrays really consist of one region."""
        pass
        
    def Show(self):
        """Show a summary of the region metadata"""
        
        print("===========================================================")
        print(" Sector:             "+str(self.res.sector[0]))
        print(" Region:             "+str(self.res.region[0]))
        
        print(" --------------------  Spectrum  -------------------------")
        self.spo.Show()
        
        print(" --------------------  Response  -------------------------")
        self.res.Show(iregion=self.res.region[0])

        
# =========================================================
# Data class
# =========================================================

class dataset:
    """The dataset class is the most general class containing a 
       dataset with multiple regions. Using this class, users
       can read, write and manipulate spectral datasets."""
 
    def __init__(self):
        self.regions=[]

    # -----------------------------------------------------
    # Read one region from a spo and res file.
    # -----------------------------------------------------
    
    def ReadRegion(self,iregion,spofile,resfile):
        """Read one region with number iregion from the two SPEX files."""
        
        # Read the spo and res files in a temporary object
        tspo=spo()
        tspo.ReadFile(spofile)
        
        tres=res()
        tres.ReadFile(resfile)
        
        # Create new region
        reg=region()
        
        # Return desired region and save into local region object
        reg.spo=tspo.ReturnRegion(iregion)
        reg.res=tres.ReturnRegion(iregion)       
        
        # Adapt region number to local set
        reg.res.region=reg.res.region+len(self.regions)
        
        # Run consistency checks
        reg.Check()
        
        # Add region to list of regions
        self.regions.append(reg)


    # -----------------------------------------------------
    # Read all the regions from a spo and res file.
    # -----------------------------------------------------

    def ReadAllRegions(self,spofile,resfile):
        """Read all the regions from a spo and res file."""
        
        # Read the spo and res files in a temporary object
        tspo=spo()
        tspo.ReadFile(spofile)
        
        tres=res()
        tres.ReadFile(resfile)
        
        # Check if the number of regions in both files are the same
        if (tspo.nregion!=tres.nregion):
          print("Error: the spo and res files do not have the same number of regions!")
          return
    
        for i in np.arange(tspo.nregion):
          # Initialize a new region
          reg=region()
        
          reg.spo=tspo.ReturnRegion(i+1)
          reg.res=tres.ReturnRegion(i+1)
          
          reg.res.region=reg.res.region+len(self.regions)
        
          # Run consistency checks
          reg.Check()
        
          # Add region to list of regions
          self.regions.append(reg)


    # -----------------------------------------------------
    # Write one region to a spo and res file.
    # -----------------------------------------------------
    
    def WriteRegion(self,spofile,resfile,iregion):
        """Write one region to a spo and res file."""

        if (iregion<=len(self.regions) and iregion>0):
          self.regions[iregion-1].spo.WriteFile(spofile)
          self.regions[iregion-1].res.WriteFile(resfile)
        else:
          print("Error: region number not found!")

    # -----------------------------------------------------
    # Write all the regions to a spo and res file.
    # -----------------------------------------------------
    
    def WriteAllRegions(self,spofile,resfile):
        """Write all regions in the data object to spo and res. """
        tspo=spo()
        tres=res()
        
        i=1
        for ireg in self.regions:
          tspo.AddSpoRegion(ireg.spo)
          tres.AddResRegion(ireg.res,i)
          tres.region
          i=i+1

        tspo.WriteFile(spofile)
        tres.WriteFile(resfile)
    
    # -----------------------------------------------------
    # Show a summary of the dataset, similar to data show in SPEX
    # -----------------------------------------------------

    def Show(self):
        """Show a summary for the entire dataset"""
        for ireg in np.arange(len(self.regions)):
          self.regions[ireg].Show()
    
    
    def AddOGIP(self):
        """This function needs HEASP to run!"""
        if not _has_heasp:
          raise ImportError("HEASP module from HEASOFT is required to do this.")    
        pass
        # To be implemented...


# =========================================================
# Finally, a trick to run the module from the command line
# as an executable for testing purposes.
# =========================================================

if __name__ == "__main__":
    dat=dataset()
    dat.ReadAllRegions("rgs.spo","rgs.res")
    dat.Show()
    dat.WriteRegion("rgs_test.spo","rgs_test.res",1)
    
    
