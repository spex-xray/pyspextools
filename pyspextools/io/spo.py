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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyspextools.messages as message
import astropy.io.fits as fits
import numpy as np
import datetime
import os

# Stuff to import for compatibility between python 2 and 3

from builtins import int

from future import standard_library

standard_library.install_aliases()


# =========================================================
# The spo class contains the spectral information for one
# spo file. This file can contain multiple spectra (regions).
# =========================================================

class Spo:
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
        self.sponame = ''
        self.empty = True

        # Initialize the 'SPEX_REGIONS' table
        self.nregion = 0  #: Number of regions
        self.nchan = np.array([], dtype=int)  #: Number of channels

        # Initialize the 'SPEX_SPECTRUM' table
        self.echan1 = np.array([], dtype=float)  #: Lower energy bin value (keV)
        self.echan2 = np.array([], dtype=float)  #: Upper energy bin value (keV)
        self.tints = np.array([], dtype=float)  #: Exposure time (s)
        self.ochan = np.array([], dtype=float)  #: Source rate (c/s)
        self.dochan = np.array([], dtype=float)  #: Error Source rate (c/s)
        self.mbchan = np.array([], dtype=float)  #: Background rate (c/s)
        self.dbchan = np.array([], dtype=float)  #: Error Background rate (c/s)
        self.brat = np.array([], dtype=float)   #: Backscale ratio
        self.ssys = np.array([], dtype=float)  #: Systematic error fraction in ochan
        self.bsys = np.array([], dtype=float)  #: Systematic error fraction in bchan
        self.used = np.array([], dtype=bool)  #: true if data channel is used in the calculations

        #: true if first channel of a binned group, or if it is an unbinned data channel; otherwise false
        self.first = np.array([], dtype=bool)
        #: true if last channel of a binned group, or if it is an unbinned data channel; otherwise false
        self.last = np.array([], dtype=bool)

        # New feature since SPEX 3.05.00
        self.brat_exist = False                 #: Does the Exp_rate column exist?

        # Does the channel order need to be swapped?
        self.swap = False

        # Create a dictionary with array names
        self.anames = {'echan1': 'Lower_Energy', 'echan2': 'Upper_Energy', 'tints': 'Exposure_Time',
                       'ochan': 'Source_Rate', 'dochan': 'Err_Source_Rate', 'mbchan': 'Back_Rate',
                       'dbchan': 'Err_Back_Rate', 'brat': 'Exp_Rate', 'ssys': 'Sys_Source', 'bsys': 'Sys_Back',
                       'used': 'Used', 'first': 'First', 'last': 'Last'}

        # Mask arrays for region selection
        self.mask_region = np.array([], dtype=bool)
        self.mask_spectrum = np.array([], dtype=bool)


    # -----------------------------------------------------
    # Create a spo with zeros and size nchan
    # -----------------------------------------------------
    def zero_spo(self, nchan):
        """Creates empty arrays of size nchan."""
        self.echan1 = np.zeros(nchan, dtype=float)
        self.echan2 = np.zeros(nchan, dtype=float)
        self.tints = np.zeros(nchan, dtype=float)
        self.ochan = np.zeros(nchan, dtype=float)
        self.dochan = np.zeros(nchan, dtype=float)
        self.mbchan = np.zeros(nchan, dtype=float)
        self.dbchan = np.zeros(nchan, dtype=float)
        self.brat = np.zeros(nchan, dtype=float)
        self.ssys = np.zeros(nchan, dtype=float)
        self.bsys = np.zeros(nchan, dtype=float)
        self.used = np.ones(nchan, dtype=bool)
        self.first = np.ones(nchan, dtype=bool)
        self.last = np.ones(nchan, dtype=bool)

    # -----------------------------------------------------
    # Functions to add spectra to the spo file
    # -----------------------------------------------------

    def add_spo_region(self, origspo, iregion=1):
        """Function to add spectrum regions to a spo file."""

        stat = origspo.get_mask(iregion)
        if stat != 0:
            print("Error: Cannot select region.")
            return -1

        mask = origspo.mask_region
        self.nchan = np.append(self.nchan, origspo.nchan[mask])

        mask = origspo.mask_spectrum
        self.echan1 = np.append(self.echan1, origspo.echan1[mask])
        self.echan2 = np.append(self.echan2, origspo.echan2[mask])
        self.tints = np.append(self.tints, origspo.tints[mask])
        self.ochan = np.append(self.ochan, origspo.ochan[mask])
        self.dochan = np.append(self.dochan, origspo.dochan[mask])
        self.mbchan = np.append(self.mbchan, origspo.mbchan[mask])
        self.dbchan = np.append(self.dbchan, origspo.dbchan[mask])
        self.brat = np.append(self.brat, origspo.brat[mask])
        self.ssys = np.append(self.ssys, origspo.ssys[mask])
        self.bsys = np.append(self.bsys, origspo.bsys[mask])
        self.used = np.append(self.used, origspo.used[mask])
        self.first = np.append(self.first, origspo.first[mask])
        self.last = np.append(self.last, origspo.last[mask])

        self.empty = False

    # -----------------------------------------------------
    # Function to remove a region from a spectrum
    # -----------------------------------------------------

    def del_spo_region(self, iregion):
        """Remove spectrum from region with number 'iregion'"""

        stat = self.get_mask(iregion)
        if stat != 0:
            print("Error: Cannot select region.")
            return -1

        mask = np.invert(self.mask_region)
        self.nchan = self.nchan[mask]

        mask = np.invert(self.mask_spectrum)
        self.echan1 = self.echan1[mask]
        self.echan2 = self.echan2[mask]
        self.tints = self.tints[mask]
        self.ochan = self.ochan[mask]
        self.dochan = self.dochan[mask]
        self.mbchan = self.mbchan[mask]
        self.dbchan = self.dbchan[mask]
        self.brat = self.brat[mask]
        self.ssys = self.ssys[mask]
        self.bsys = self.bsys[mask]
        self.used = self.used[mask]
        self.first = self.first[mask]
        self.last = self.last[mask]

        self.nregion = self.nregion - 1

        if self.nregion == 0:
            self.empty = True

    # -----------------------------------------------------
    # Function to read spectrum from a .spo file
    # -----------------------------------------------------

    def read_file(self, spofile):
        """ Function to read a spectrum from a .spo file."""

        # The filename is saved in the data object for reference.
        self.sponame = spofile

        # Open the .spo file with astropy.io.fits and open the table and header 
        # information in the SPEX_REGIONS extension in the FITS file.
        spofile = fits.open(self.sponame)
        table = spofile['SPEX_REGIONS'].data
        header = spofile['SPEX_REGIONS'].header

        # Read the number of regions in the .spo file 
        # (equal to the number of spectra)
        self.nregion = header['NAXIS2']

        # The SPEX_REGIONS table in the spo file contains the number of channels for
        # each spectrum. Here, we append the table from the spo file to the nchan 
        # array to save these numbers in the object 
        self.nchan = np.append(self.nchan, table['NCHAN'])

        # Now, we open the SPEX_SPECTRUM extension in the .spo file 
        # which contains the actual spectra.
        table = spofile['SPEX_SPECTRUM'].data
        cols = spofile['SPEX_SPECTRUM'].columns

        # Copy all the table columns
        self.echan1 = table['Lower_Energy']
        self.echan2 = table['Upper_Energy']
        self.tints = table['Exposure_Time']
        self.ochan = table['Source_Rate']
        self.dochan = table['Err_Source_Rate']
        self.mbchan = table['Back_Rate']
        self.dbchan = table['Err_Back_Rate']
        self.ssys = table['Sys_Source']
        self.bsys = table['Sys_Back']
        self.used = table['Used']
        self.first = table['First']
        self.last = table['Last']

        for col in cols.names:
            if col == "Exp_Rate":
                self.brat = table['Exp_Rate']
                self.brat_exist = True

        if not self.brat_exist:
            self.brat = np.ones(self.ochan.size, dtype=float)

        # Close the .spo file
        spofile.close()

        self.empty = False

    # -----------------------------------------------------
    # Function to return one spectrum for one region
    # -----------------------------------------------------

    def return_region(self, iregion):
        """Function to return a spo object with containing the
           spectrum of the region with number 'iregion'. """
        stat = self.get_mask(iregion)
        if stat != 0:
            print("Error: Cannot select region.")
            return -1

        # Check if object is empty
        if self.empty:
            print("Error: Response object empty.")
            return -1

        sporeg = Spo()

        mask = self.mask_region
        sporeg.nchan = self.nchan[mask]

        mask = self.mask_spectrum
        sporeg.echan1 = self.echan1[mask]
        sporeg.echan2 = self.echan2[mask]
        sporeg.tints = self.tints[mask]
        sporeg.ochan = self.ochan[mask]
        sporeg.dochan = self.dochan[mask]
        sporeg.mbchan = self.mbchan[mask]
        sporeg.dbchan = self.dbchan[mask]
        sporeg.brat = self.brat[mask]
        sporeg.ssys = self.ssys[mask]
        sporeg.bsys = self.bsys[mask]
        sporeg.used = self.used[mask]
        sporeg.first = self.first[mask]
        sporeg.last = self.last[mask]

        sporeg.sponame = self.sponame
        sporeg.empty = False
        sporeg.check()

        return sporeg

    # -----------------------------------------------------
    # Function to write all spectra to a .spo file
    # -----------------------------------------------------

    def write_file(self, sponame, exp_rate=False, overwrite=False, history=None):
        """Function to write the spectrum to a .spo file with the name 'sponame'.
        The exp_rate flag determines whether the Exp_Rate column is added containing
        the ratio between the backscales of the source and background spectra. This column
        can only be read by SPEX >=3.05.00."""

        # First check whether object is complete and consistent
        good = self.check()

        if good == -1:
            print("Error: Object is not internally consistent!")
            print("Check the object structure.")
            return -1

        # Create a primary header
        prihdr = fits.Header()
        prihdr['CREATOR'] = 'pyspextools python module'
        prihdr['ORIGIN'] = 'SRON Netherlands Institute for Space Research'

        now = datetime.datetime.now()
        prihdr['HISTORY'] = "Created on: {0}".format(str(now))
        if history is not None:
            for line in history:
                prihdr['HISTORY'] = line

        prihdu = fits.PrimaryHDU(header=prihdr)

        # Create the SPEX_REGIONS extension
        col1 = fits.Column(name='NCHAN', format='1J', array=self.nchan)
        cols = fits.ColDefs([col1])

        tb_regions = fits.BinTableHDU.from_columns(cols)
        tb_regions.header['EXTNAME'] = 'SPEX_REGIONS'

        # Then create the SPEX_SPECTRUM extension
        col1 = fits.Column(name='Lower_Energy', format='1D', unit='keV', array=self.echan1)
        col2 = fits.Column(name='Upper_Energy', format='1D', unit='keV', array=self.echan2)
        col3 = fits.Column(name='Exposure_Time', format='1E', unit='s', array=self.tints)
        col4 = fits.Column(name='Source_Rate', format='1E', unit='c/s', array=self.ochan)
        col5 = fits.Column(name='Err_Source_Rate', format='1E', unit='c/s', array=self.dochan)
        col6 = fits.Column(name='Back_Rate', format='1E', unit='c/s', array=self.mbchan)
        col7 = fits.Column(name='Err_Back_Rate', format='1E', unit='c/s', array=self.dbchan)

        if exp_rate:
            col8 = fits.Column(name='Exp_Rate', format='1E', unit='', array=self.brat)
            col9 = fits.Column(name='Sys_Source', format='1E', unit='', array=self.ssys)
            col10 = fits.Column(name='Sys_Back', format='1E', unit='', array=self.bsys)
            col11 = fits.Column(name='First', format='1L', unit='', array=self.first)
            col12 = fits.Column(name='Last', format='1L', unit='', array=self.last)
            col13 = fits.Column(name='Used', format='1L', unit='', array=self.used)

            cols = fits.ColDefs([col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13])
        else:
            col8 = fits.Column(name='Sys_Source', format='1E', unit='', array=self.ssys)
            col9 = fits.Column(name='Sys_Back', format='1E', unit='', array=self.bsys)
            col10 = fits.Column(name='First', format='1L', unit='', array=self.first)
            col11 = fits.Column(name='Last', format='1L', unit='', array=self.last)
            col12 = fits.Column(name='Used', format='1L', unit='', array=self.used)

            cols = fits.ColDefs([col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12])

        tb_spectrum = fits.BinTableHDU.from_columns(cols)
        tb_spectrum.header['EXTNAME'] = 'SPEX_SPECTRUM'

        # Combine the extentions into one list
        thdulist = fits.HDUList([prihdu, tb_regions, tb_spectrum])

        # Write hdulist to file
        try:
            thdulist.writeto(sponame, overwrite=overwrite)
        except IOError:
            print("Error: File {0} already exists. I will not overwrite it!".format(sponame))
            return 1

        return 0

    # -----------------------------------------------------
    # Swap/Flip arrays between energy or wavelength order
    # -----------------------------------------------------
    def swap_order(self):
        """Swap the channel order of the spectrum between wavelength or energy order. This is
        for example helpful for grating spectra, which are originally stored in wavelength order
        but must be flipped to energy order in SPEX format. """

        # Loop over columns in SPO object and swap/flip arrays
        for var in self.anames.keys():
            if hasattr(self, var):
                inarr = getattr(self, var)
                setattr(self, var, np.flip(inarr, 0))

    # -----------------------------------------------------
    # Sanity check whether object is complete and consistent
    # -----------------------------------------------------

    def check(self):
        """Perform several checks whether the information in the spectrum is consistent. """

        # Check if nchan is numpy array
        if not isinstance(self.nchan, np.ndarray):
            print("Error: NCHAN is not a numpy array.")
            return -1

        # Check if all the columns have the right length
        total = np.sum(self.nchan)

        for name in self.anames.keys():
            array = getattr(self, name)
            if array.size != total:
                print("Error: " + self.anames[name] + " array length not consistent!")
                print("According to nchan the length should be: {0}".format(total))
                print("The actual array length is:              {0}".format(array.size))
                return -1

        # Check the arrays for consistency

        for ireg in np.arange(self.nregion):
            fchan = sum(self.nchan[0:ireg]) - self.nchan[ireg]
            for ichan in np.arange(self.nchan[ireg]) + fchan:
                if self.echan2[ichan] <= self.echan1[ichan]:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "does not have a positive width.".format(ichan-fchan+1, ireg+1))
                    return -1
                if self.echan1[ichan] < 0.0:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "has a negative lower limit.".format(ichan-fchan+1, ireg+1))
                    return -1
                if self.dochan[ichan] < 0.0:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "has a negative error.".format(ichan-fchan+1, ireg+1))
                    return -1
                if self.ssys[ichan] < 0.0:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "has a negative systematic error.".format(ichan-fchan+1, ireg+1))
                    return -1
                if self.bsys[ichan] < 0.0:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "has a negative background systematic error.".format(ichan-fchan+1, ireg+1))
                    return -1
                if self.tints[ichan] < 0.0:
                    message.error("Bin number {0} in spectrum region {1} "
                                  "has a negative exposure time.".format(ichan-fchan+1, ireg+1))
                    return -1

        return 0


    # -----------------------------------------------------
    # Function to check the spo file name for correct extension
    # -----------------------------------------------------

    def check_filename(self,filename):
        """Check if the output filename has the correct .spo extension. The method returns a correct file name."""
        sponame, spo_extension = os.path.splitext(filename)
        if spo_extension != ".spo":
            message.warning("Output filename does not have the correct .spo extension.")
            print("Renaming file to end with '.spo'.")
            print("")
            spofile = sponame + '.spo'
        else:
            spofile = filename

        return spofile

    # -----------------------------------------------------
    # Create a mask for a spo region selection
    #
    # Since a spo file lists all the spectra in a single
    # table, we must find the rows where a particular 
    # spectrum or region begins and ends.
    # -----------------------------------------------------

    def get_mask(self, iregion):
        """Create a mask to select spectral information for one region only. """
        # Python counts from 0, so create adequate counter
        ireg = iregion - 1

        # Check if iregion is in an allowed range
        if (iregion >= self.nregion) and (iregion < 1):
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

        self.mask_spectrum[frow:lrow] = True

        return 0

    # -----------------------------------------------------
    # Show a summary of the spo file, similar to data show in SPEX
    # -----------------------------------------------------

    def show(self, iregion=1):
        """Show some basic properties of the spectrum."""

        tspo = self.return_region(iregion)

        print(" Original spo file                      :  {0}".format(tspo.sponame))
        print(" Number of data channels                :  {0}".format(tspo.nchan[0]))
        print(" Data energy range                      :  {0:.2f} - {1:.2f} keV".format(np.min(tspo.echan1),
                                                                                        np.max(tspo.echan2)))
        print(" Exposure time mean                     :  {0:.2f} s".format(np.mean(tspo.tints)))
