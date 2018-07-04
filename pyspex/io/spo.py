#!/usr/bin/env python

# =========================================================
"""
  Python module to read and write SPEX spo files.
  SPEX spo files contain (background subtracted) spectra
  See this page for the format specification: 
      
    http://var.sron.nl/SPEX-doc/manualv3.04/manualse108.html#x122-2840008.2
  
  This file contains the spo class
 
  Dependencies:
    - astropy.io.fits:     Read and write FITS files
    - numpy:               Array operations
"""
# =========================================================

# Stuff to import for compatibility between python 2 and 3
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object


import astropy.io.fits as fits
import numpy as np

# =========================================================
# The spo class contains the spectral information for one
# spo file. This file can contain multiple spectra (regions).
# =========================================================

class spo:
    """The spo class contains the spectral information for one
       spo file. This file can contain multiple spectra (regions). 
       A call to spo() sets the variables that will contain 
       the spectral information."""
    
    # -----------------------------------------------------
    # Function to initialize the spo object
    # -----------------------------------------------------
    # The 'add_' functions below are used to fill the arrays with information.  
    #

    def __init__(self):
        
        # Initialize spo filename
        self.sponame=''
        self.empty=True
        
        # Initialize the 'SPEX_REGIONS' table
        self.nregion=0                             #: Number of regions
        self.nchan =np.array([],dtype=int)          #: Number of channels 
        
        # Initialize the 'SPEX_SPECTRUM' table
        self.echan1= np.array([],dtype=float)        #: Lower energy bin value (keV)
        self.echan2= np.array([],dtype=float)        #: Upper energy bin value (keV)
        self.tints = np.array([],dtype=float)        #: Exposure time (s)
        self.ochan = np.array([],dtype=float)        #: Source rate (c/s)
        self.dochan= np.array([],dtype=float)        #: Error Source rate (c/s)
        self.mbchan= np.array([],dtype=float)        #: Background rate (c/s)
        self.dbchan= np.array([],dtype=float)        #: Error Background rate (c/s)
        self.ssys  = np.array([],dtype=float)        #: Systematic error fraction in ochan
        self.bsys  = np.array([],dtype=float)        #: Systematic error fraction in bchan
        self.used  = np.array([],dtype=bool)         #: true if data channel is used in the calculations
        self.first = np.array([],dtype=bool)         #: true if first channel of a binned group, or if it is an unbinned data channel; otherwise false
        self.last  = np.array([],dtype=bool)         #: true if last channel of a binned group, or if it is an unbinned data channel; otherwise false

        
        # Create a dictionary with array names
        self.anames={}
        self.anames['echan1']='Lower_Energy'
        self.anames['echan2']='Upper_Energy'
        self.anames['tints'] ='Exposure_Time'
        self.anames['ochan'] ='Source_Rate' 
        self.anames['dochan']='Err_Source_Rate'
        self.anames['mbchan']='Back_Rate'
        self.anames['dbchan']='Err_Back_Rate'
        self.anames['ssys']  ='Sys_Source'
        self.anames['bsys']  ='Sys_Back'
        self.anames['used']  ='Used'
        self.anames['first'] ='First'
        self.anames['last']  ='Last'
    
    
    # -----------------------------------------------------
    # Functions to add spectra to the spo file
    # -----------------------------------------------------
     
    def AddSpoRegion(self,origspo,iregion=1):
        """Function to add spectrum regions to a spo file."""
    
        stat=origspo.GetMask(iregion)
        if (stat!=0):
          print("Error: Cannot select region.")
          return -1

        mask=origspo.mask_region
        self.nchan  = np.append(self.nchan,origspo.nchan[mask])   
        
        mask=origspo.mask_spectrum
        self.echan1 = np.append(self.echan1,origspo.echan1[mask])  
        self.echan2 = np.append(self.echan2,origspo.echan2[mask])  
        self.tints  = np.append(self.tints,origspo.tints[mask])    
        self.ochan  = np.append(self.ochan,origspo.ochan[mask])   
        self.dochan = np.append(self.dochan,origspo.dochan[mask]) 
        self.mbchan = np.append(self.mbchan,origspo.mbchan[mask]) 
        self.dbchan = np.append(self.dbchan,origspo.dbchan[mask]) 
        self.ssys   = np.append(self.ssys,origspo.ssys[mask])     
        self.bsys   = np.append(self.bsys,origspo.bsys[mask])     
        self.used   = np.append(self.used,origspo.used[mask])     
        self.first  = np.append(self.first,origspo.first[mask])   
        self.last   = np.append(self.last,origspo.last[mask])     
       
        self.empty=False
    
    # -----------------------------------------------------
    # Function to remove a region from a spectrum
    # -----------------------------------------------------
    
    def DelSpoRegion(self,iregion):
        """Remove spectrum from region with number 'iregion'"""   
    
        stat=self.GetMask(iregion)
        if (stat!=0):
          print("Error: Cannot select region.")
          return -1
    
        mask = np.invert(self.mask_region)
        self.nchan = self.nchan[mask]
        
        mask = np.invert(self.mask_spectrum)
        self.echan1 = self.echan1[mask]  
        self.echan2 = self.echan2[mask]  
        self.tints  = self.tints[mask]    
        self.ochan  = self.ochan[mask]   
        self.dochan = self.dochan[mask] 
        self.mbchan = self.mbchan[mask] 
        self.dbchan = self.dbchan[mask] 
        self.ssys   = self.ssys[mask]     
        self.bsys   = self.bsys[mask]     
        self.used   = self.used[mask]     
        self.first  = self.first[mask]   
        self.last   = self.last[mask]     
        
        self.nregion=self.nregion-1
        
        if (self.nregion==0):
          self.empty=True

        
    # -----------------------------------------------------
    # Function to read spectrum from a .spo file
    # -----------------------------------------------------
    
    def ReadFile(self,spofile):
        """ Function to read a spectrum from a .spo file."""
        
        # The filename is saved in the data object for reference.
        self.sponame = spofile
        
        # Open the .spo file with astropy.io.fits and open the table and header 
        # information in the SPEX_REGIONS extension in the FITS file.
        spofile = fits.open(self.sponame)
        table   = spofile['SPEX_REGIONS'].data
        header  = spofile['SPEX_REGIONS'].header
        
        # Read the number of regions in the .spo file 
        # (equal to the number of spectra)
        self.nregion = header['NAXIS2']
        
        # The SPEX_REGIONS table in the spo file contains the number of channels for
        # each spectrum. Here, we append the table from the spo file to the nchan 
        # array to save these numbers in the object 
        self.nchan      = np.append(self.nchan,table['NCHAN']) 
        
        # Now, we open the SPEX_SPECTRUM extension in the .spo file 
        # which contains the actual spectra.
        table = spofile['SPEX_SPECTRUM'].data
        
        # Copy all the table columns
        self.echan1 = table['Lower_Energy']
        self.echan2 = table['Upper_Energy']
        self.tints  = table['Exposure_Time']
        self.ochan  = table['Source_Rate']
        self.dochan = table['Err_Source_Rate']
        self.mbchan = table['Back_Rate']
        self.dbchan = table['Err_Back_Rate']
        self.ssys   = table['Sys_Source']
        self.bsys   = table['Sys_Back']
        self.used   = table['Used']
        self.first  = table['First']
        self.last   = table['Last']       
        
        # Close the .spo file
        spofile.close()
        
        self.empty=False

    # -----------------------------------------------------
    # Function to return one spectrum for one region
    # -----------------------------------------------------
    
    def ReturnRegion(self,iregion):
        """Function to return a spo object with containing the
           spectrum of the region with number 'iregion'. """
        stat=self.GetMask(iregion)
        if (stat!=0):
          print("Error: Cannot select region.")
          return -1

        # Check if object is empty
        if (self.empty):
          print("Error: Response object empty.")
          return -1
        
        sporeg = spo()
        
        mask = self.mask_region
        sporeg.nchan = self.nchan[mask]
        
        mask = self.mask_spectrum
        sporeg.echan1 = self.echan1[mask]  
        sporeg.echan2 = self.echan2[mask]  
        sporeg.tints  = self.tints[mask]    
        sporeg.ochan  = self.ochan[mask]   
        sporeg.dochan = self.dochan[mask] 
        sporeg.mbchan = self.mbchan[mask] 
        sporeg.dbchan = self.dbchan[mask] 
        sporeg.ssys   = self.ssys[mask]     
        sporeg.bsys   = self.bsys[mask]     
        sporeg.used   = self.used[mask]     
        sporeg.first  = self.first[mask]   
        sporeg.last   = self.last[mask]     
        
        sporeg.sponame= self.sponame
        sporeg.empty  = False
        sporeg.Check()
        
        return sporeg


    # -----------------------------------------------------
    # Function to write all spectra to a .spo file
    # -----------------------------------------------------
    
    def WriteFile(self,sponame):
        """Function to write the spectrum to a .spo file with the name 'sponame'. """
        # First check whether object is complete and consistent
        good=self.Check()
        
        if (good==-1):
           print("Error: Object is not internally consistent!")
           print("Check the object structure.")
           return -1
                
        # Create a primary header
        prihdr = fits.Header()
        prihdr['CREATOR'] = 'pyspex python module'
        prihdr['ORIGIN'] = 'SRON Netherlands Institute for Space Research'
        prihdu = fits.PrimaryHDU(header=prihdr)
                
        # Create the SPEX_REGIONS extension
        col1 = fits.Column(name='NCHAN', format='1J', array=self.nchan)
        cols = fits.ColDefs([col1])
        
        tb_regions = fits.BinTableHDU.from_columns(cols)
        tb_regions.header['EXTNAME'] = 'SPEX_REGIONS'
                
        # Then create the SPEX_SPECTRUM extension
        col1=fits.Column(name='Lower_Energy', format='1D', unit='keV', array=self.echan1)
        col2=fits.Column(name='Upper_Energy', format='1D', unit='keV', array=self.echan2)
        col3=fits.Column(name='Exposure_Time', format='1E', unit='s', array=self.tints)
        col4=fits.Column(name='Source_Rate', format='1E', unit='c/s', array=self.ochan)
        col5=fits.Column(name='Err_Source_Rate', format='1E', unit='c/s', array=self.dochan)
        col6=fits.Column(name='Back_Rate', format='1E', unit='c/s', array=self.mbchan)
        col7=fits.Column(name='Err_Back_Rate', format='1E', unit='c/s', array=self.dbchan)
        col8=fits.Column(name='Sys_Source', format='1E', unit='', array=self.ssys)
        col9=fits.Column(name='Sys_Back', format='1E', unit='', array=self.bsys)
        col10=fits.Column(name='First', format='1L', unit='', array=self.first)
        col11=fits.Column(name='Last', format='1L', unit='', array=self.last)
        col12=fits.Column(name='Used', format='1L', unit='', array=self.used)
        
        cols=fits.ColDefs([col1,col2,col3,col4,col5,col6,col7,col8,col9,col10,col11,col12])
    
        tb_spectrum = fits.BinTableHDU.from_columns(cols)
        tb_spectrum.header['EXTNAME']='SPEX_SPECTRUM'
            
        # Combine the extentions into one list
        thdulist = fits.HDUList([prihdu, tb_regions, tb_spectrum])
            
        # Write hdulist to file
        thdulist.writeto(sponame)
   
   
    # -----------------------------------------------------
    # Sanity check whether object is complete and consistent
    # -----------------------------------------------------
    
    def Check(self):
        """Perform several checks whether the information in the spectrum is consistent. """
        # Check if all the columns have the right length
        total=self.nchan.sum()
        
        for name in self.anames.keys():
            array=getattr(self,name)
            if (array.size!=total):
              print("Error: "+self.anames[name]+" array length not consistent!")
              return -1

    # -----------------------------------------------------
    # Create a mask for a spo region selection
    #
    # Since a spo file lists all the spectra in a single
    # table, we must find the rows where a particular 
    # spectrum or region begins and ends.
    # -----------------------------------------------------
    
    def GetMask(self,iregion):
        """Create a mask to select spectral information for one region only. """
        # Python counts from 0, so create adequate counter
        ireg=iregion-1
        
        # Check if iregion is in an allowed range
        if (iregion>=self.nregion) and (iregion<1):
          print("Error: Requested region not available.")
          return -1
        
        # Mark region in SPEX_REGION extension
        self.mask_region = np.full(len(self.nchan), False, dtype=bool)
        self.mask_region[ireg] = True
        
        # Select region in SPEX SPECTRUM table
        self.mask_spectrum = np.full(len(self.echan1), False, dtype=bool)
        
        # Initialize first and last row  
        frow = 0   
        lrow = 0 
        
        # Count the channels 
        for i in np.arange(iregion): 
          frow = lrow
          lrow = lrow + self.nchan[i]
        
        self.mask_spectrum[frow:lrow]=True
        
        return 0

    # -----------------------------------------------------
    # Show a summary of the spo file, similar to data show in SPEX
    # -----------------------------------------------------

    def Show(self,iregion=1):
        """Show some basic properties of the spectrum."""
        
        tspo = self.ReturnRegion(iregion)
        
        print(" Original spo file                      :  {0}".format(tspo.sponame))
        print(" Number of data channels                :  {0}".format(tspo.nchan[0]))
        print(" Data energy range                      :  {0:.2f} - {1:.2f} keV".format(np.min(tspo.echan1),np.max(tspo.echan2)))
        print(" Exposure time mean                     :  {0:.2f} s".format(np.mean(tspo.tints)))




# =========================================================
# Finally, a trick to run the module from the command line
# as an executable for testing purposes.
# =========================================================

if __name__ == "__main__":
    test=spo()
    test.ReadFile("rgs.spo")
    test.DelSpoRegion(1)
    test.WriteFile("rgs_test.spo")
