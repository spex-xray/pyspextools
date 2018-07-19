#!/usr/bin/env python

# =========================================================
"""
  Python module to read and write SPEX res files.
  SPEX res files contain the response matrix and effective area
  See this page for the format specification: 
      
    http://var.sron.nl/SPEX-doc/manualv3.04/manualse108.html#x122-2840008.2
  
  This file contains the res class
 
  Dependencies:
    - astropy.io.fits:     Read and write FITS files
    - numpy:               Array operations
"""
# =========================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import astropy.io.fits as fits
import numpy as np

# Stuff to import for compatibility between python 2 and 3

from builtins import int

from future import standard_library

standard_library.install_aliases()


# =========================================================
# The res class contains the response information for one
# res file. This file can contain multiple responses (regions).
# =========================================================

class Res:
    """The res class contains the response information for one
       res file. This file can contain multiple responses (regions)."""

    def __init__(self):

        self.resname = ''
        self.empty = True

        # Response components (SPEX_RESP_ICOMP)
        self.nchan = np.array([], dtype=int)  #: Number of channels
        self.neg = np.array([], dtype=int)  #: Number of energy bins
        self.sector = np.array([], dtype=int)  #: Sectors
        self.region = np.array([], dtype=int)  #: Regions
        self.shcomp = np.array([], dtype=int)  #: Shared components (optional)

        self.nsector = 0  #: Number of sectors
        self.nregion = 0  #: Number of regions
        self.ncomp = 0  #: Number of response components

        self.share_comp = False  #: Are there shared components (?)
        self.area_scal = False  #: Is there areascal information (?)
        self.resp_der = False  #: Are there response derivatives (?)

        # Response groups (SPEX_RESP_GROUP)
        self.eg1 = np.array([], dtype=float)  #: start energy for group (keV)
        self.eg2 = np.array([], dtype=float)  #: end energy for group (keV)
        self.ic1 = np.array([], dtype=int)  #: Start channel for response group
        self.ic2 = np.array([], dtype=int)  #: End channel for response group
        self.nc = np.array([], dtype=int)  #: Number of data channels in group
        self.relarea = np.array([], dtype=float)  #: Area scaling factors

        # Response values (SPEX_RESP_RESP)
        self.resp = np.array([], dtype=float)  #: response values for group (m**2)
        self.dresp = np.array([], dtype=float)  #: response derivatives for group (optional)

        # Mask arrays
        self.mask_resp = np.array([], dtype=bool)
        self.mask_group = np.array([], dtype=bool)
        self.mask_icomp = np.array([], dtype=bool)

        # Should channel order be swapped?
        self.swap = False

    # -----------------------------------------------------
    # Function to add a response from another region
    # -----------------------------------------------------

    def add_res_region(self, origres, iregion=1):
        """Function to add region(s) to a response."""

        stat = origres.GetMask(iregion)
        if stat != 0:
            print("Error: Cannot select region.")
            return -1

        # If object is still empty, there cannot be conflicts, so set
        # the logicals to the input values:
        if self.empty:
            self.share_comp = origres.share_comp
            self.area_scal = origres.area_scal
            self.resp_der = origres.resp_der

        # Check whether the existing settings are compatible with the response
        # being added:
        if self.share_comp != origres.share_comp:
            print("Error: Share_comp setting of added response is different from ")
            print("the existing response. The matrices are incompatible.")
            return -1

        if self.area_scal != origres.area_scal:
            print("Error: Areascal setting of added response is different from ")
            print("the existing response. The matrices are incompatible.")
            return -1

        if self.resp_der != origres.resp_der:
            print("Error: Response derivative setting of added response is different from ")
            print("the existing response. The matrices are incompatible.")
            return -1

        # Append the response information to the arrays
        self.nchan = np.append(self.nchan, origres.nchan[origres.mask_icomp])
        self.neg = np.append(self.neg, origres.neg[origres.mask_icomp])
        self.sector = np.append(self.sector, origres.sector[origres.mask_icomp])
        self.region = np.append(self.region, origres.region[origres.mask_icomp])
        if self.share_comp:
            self.shcomp = np.append(self.shcomp, origres.shcomp[origres.mask_icomp])

        # Append the response groups (SPEX_RESP_GROUP)
        self.eg1 = np.append(self.eg1, origres.eg1[origres.mask_group])
        self.eg2 = np.append(self.eg2, origres.eg2[origres.mask_group])
        self.ic1 = np.append(self.ic1, origres.ic1[origres.mask_group])
        self.ic2 = np.append(self.ic2, origres.ic2[origres.mask_group])
        self.nc = np.append(self.nc, origres.nc[origres.mask_group])
        if self.relarea:
            self.relarea = np.append(self.relarea, origres.relarea[origres.mask_group])

        # Append the response values (SPEX_RESP_RESP)
        self.resp = np.append(self.resp, origres.resp[origres.mask_resp])
        if self.resp_der:
            self.dresp = np.append(self.dresp, origres.dresp[origres.mask_resp])

        self.nregion = self.nregion + origres.nregion
        self.ncomp = self.ncomp + origres.ncomp
        self.nsector = np.max(self.sector)

        print("Response added.")
        print("Please check if the sector structure is correct before saving the file.")

        if self.empty:
            self.empty = False

    # -----------------------------------------------------
    # Function to remove a region from a response
    # -----------------------------------------------------

    def del_res_region(self, iregion):
        """Remove region with number 'iregion'."""

        stat = self.get_mask(iregion)
        if stat != 0:
            print("Error: Cannot remove region.")
            return -1

        mask = np.invert(self.mask_resp)
        self.resp = self.resp[mask]
        if self.resp_der:
            self.dresp = self.dresp[mask]

        # Remove groups in SPEX_RESP_GROUP
        mask = np.invert(self.mask_group)
        self.eg1 = self.eg1[mask]
        self.eg2 = self.eg2[mask]
        self.ic1 = self.ic1[mask]
        self.ic2 = self.ic2[mask]
        self.nc = self.nc[mask]
        if self.area_scal:
            self.relarea = self.relarea[mask]

        # Remove groups in SPEX_RESP_ICOMP
        mask = np.invert(self.mask_icomp)
        self.nchan = self.nchan[mask]
        self.neg = self.neg[mask]
        self.sector = self.sector[mask]
        self.region = self.region[mask]
        if self.share_comp:
            self.shcomp = self.shcomp[mask]

        # Fix the number of regions and sectors
        icomp_trailing_rows = np.where(self.region > iregion)[0]
        for i in icomp_trailing_rows:
            self.region[i] = self.region[i] - 1

        self.nregion = self.nregion - 1

        return 0

    # -----------------------------------------------------
    # Function to read a response from a .res file
    # -----------------------------------------------------

    def read_file(self, resfile):
        """Function to read a response from a .res file."""

        # The filename is saved in the data object for reference.
        self.resname = resfile

        # Open the .res file with astropy.io.fits 
        resfile = fits.open(self.resname)

        table = resfile['SPEX_RESP_ICOMP'].data
        header = resfile['SPEX_RESP_ICOMP'].header

        # Read number of sectors, regions and components
        self.nsector = header['NSECTOR']
        self.nregion = header['NREGION']
        self.ncomp = header['NCOMP']

        self.share_comp = header['SHARECOM']
        self.area_scal = header['AREASCAL']
        self.resp_der = header['RESPDER']

        self.nchan = table['NCHAN']
        self.neg = table['NEG']
        self.sector = table['SECTOR']
        self.region = table['REGION']
        if self.share_comp:
            self.shcomp = table['SHCOMP']

        # Read group indices from SPEX_RESP_GROUP

        table = resfile['SPEX_RESP_GROUP'].data

        self.eg1 = table['EG1']
        self.eg2 = table['EG2']
        self.ic1 = table['IC1']
        self.ic2 = table['IC2']
        self.nc = table['NC']
        if self.area_scal:
            self.relarea = table['RELAREA']

        # Read response values from SPEX_RESP_RESP

        table = resfile['SPEX_RESP_RESP'].data
        header = resfile['SPEX_RESP_RESP'].header

        if header['TTYPE1'] == "Response":
            self.resp = table['Response']
        elif header['TTYPE1'] == "RESP":
            self.resp = table['RESP']
        else:
            print("Error: Response column not found in file.")

        if self.resp_der:
            if header['TTYPE2'] == "Response_Der":
                self.dresp = table['Response_Der']
            elif header['TTYPE2'] == "DRESP":
                self.dresp = table['DRESP']
            else:
                print("Error: Response derivative column not found.")

        self.empty = False

        resfile.close()

    # -----------------------------------------------------
    # Function to return a region from a res object
    # -----------------------------------------------------

    def return_region(self, iregion):
        """Return a res object with the data from 1 selected region."""

        stat = self.get_mask(iregion)
        if stat != 0:
            print("Error: Cannot select region.")
            return -1

        # Check if object is empty
        if self.empty:
            print("Error: Response object empty.")
            return -1

        # Initialize the response object to return  
        resreg = Res()

        mask = self.mask_resp
        resreg.resp = self.resp[mask]
        if self.resp_der:
            self.dresp = self.dresp[mask]

        # Remove groups in SPEX_RESP_GROUP
        mask = self.mask_group
        resreg.eg1 = self.eg1[mask]
        resreg.eg2 = self.eg2[mask]
        resreg.ic1 = self.ic1[mask]
        resreg.ic2 = self.ic2[mask]
        resreg.nc = self.nc[mask]
        if self.area_scal:
            resreg.relarea = self.relarea[mask]

        # Remove groups in SPEX_RESP_ICOMP
        mask = self.mask_icomp
        resreg.nchan = self.nchan[mask]
        resreg.neg = self.neg[mask]
        resreg.sector = self.sector[mask]
        resreg.region = self.region[mask]
        # Return always a response with Region number 1
        resreg.region = resreg.region * 0 + 1
        if self.share_comp:
            resreg.shcomp = self.shcomp[mask]

        resreg.ncomp = len(resreg.region)
        resreg.nsector = 1
        resreg.nregion = 1

        resreg.resname = self.resname

        resreg.empty = False

        resreg.check()

        return resreg

    # -----------------------------------------------------
    # Function to write a response to a .res file
    # -----------------------------------------------------

    def write_file(self, resfile, overwrite=False):
        """Write the response information to a .res file with name 'resfile'."""

        check = self.check()
        if check != 0:
            print("Error: Response check failed.")
            return

        # Create a primary header
        prihdr = fits.Header()
        prihdr['CREATOR'] = 'pyspex python module'
        prihdr['ORIGIN'] = 'SRON Netherlands Institute for Space Research'
        prihdu = fits.PrimaryHDU(header=prihdr)

        # Create the SPEX_RESP_ICOMP extension
        col1 = fits.Column(name='NCHAN', format='1J', array=self.nchan)
        col2 = fits.Column(name='NEG', format='1J', array=self.neg)
        col3 = fits.Column(name='SECTOR', format='1J', array=self.sector)
        col4 = fits.Column(name='REGION', format='1J', array=self.region)

        if self.share_comp:
            col5 = fits.Column(name='SHCOMP', format='1J', array=self.shcomp)
            cols = fits.ColDefs([col1, col2, col3, col4, col5])
        else:
            cols = fits.ColDefs([col1, col2, col3, col4])

        tb_icomp = fits.BinTableHDU.from_columns(cols)
        tb_icomp.header['NSECTOR'] = self.nsector
        tb_icomp.header['NREGION'] = self.nregion
        tb_icomp.header['NCOMP'] = self.ncomp

        tb_icomp.header['SHARECOM'] = self.share_comp
        tb_icomp.header['AREASCAL'] = self.area_scal
        tb_icomp.header['RESPDER'] = self.resp_der

        tb_icomp.header['EXTNAME'] = 'SPEX_RESP_ICOMP'

        # Create the SPEX_RESP_GROUP extension
        col1 = fits.Column(name='EG1', format='1D', unit='keV', array=self.eg1)
        col2 = fits.Column(name='EG2', format='1D', unit='keV', array=self.eg2)
        col3 = fits.Column(name='IC1', format='1J', array=self.ic1)
        col4 = fits.Column(name='IC2', format='1J', array=self.ic2)
        col5 = fits.Column(name='NC', format='1J', array=self.nc)

        if self.area_scal:
            col6 = fits.Column(name='RELAREA', format='1J', array=self.relarea)
            cols = fits.ColDefs([col1, col2, col3, col4, col5, col6])
        else:
            cols = fits.ColDefs([col1, col2, col3, col4, col5])

        tb_group = fits.BinTableHDU.from_columns(cols)
        tb_group.header['EXTNAME'] = 'SPEX_RESP_GROUP'

        # Create the SPEX_RESP_GROUP extension
        col1 = fits.Column(name='Response', format='1E', unit='m**2', array=self.resp)
        if self.resp_der:
            col2 = fits.Column(name='Response_Der', format='1E', unit='m**2', array=self.dresp)
            cols = fits.ColDefs([col1, col2])
        else:
            cols = fits.ColDefs([col1])

        tb_resp = fits.BinTableHDU.from_columns(cols)
        tb_resp.header['EXTNAME'] = 'SPEX_RESP_RESP'

        # Combine the extentions into one list
        thdulist = fits.HDUList([prihdu, tb_icomp, tb_group, tb_resp])

        # Write hdulist to file
        try:
            thdulist.writeto(resfile, overwrite=overwrite)
        except IOError:
            print("Error: File {0} already exists. I will not overwrite it!".format(resfile))

    # -----------------------------------------------------
    # Swap the channel order between wavelength and energy order
    # -----------------------------------------------------

    def swap_order(self):
        """Swap the channel order of the response between wavelength or energy order. This is
        for example helpful for grating spectra, which are originally stored in wavelength order
        but must be flipped to energy order in SPEX format."""

        # Loop over components to swap the channel numbers
        n1=0   # Lowest channel number
        r1=0   # Index of response array

        for i in np.arange(self.ncomp):
            n2=n1+self.neg[i]
            for j in (n1 + np.arange(self.neg[i])):
                # Update group definition
                ic2 = self.nchan[i] - self.ic1[j] + 1
                ic1 = self.nchan[i] - self.ic2[j] + 1

                self.ic1[j] = ic1
                self.ic2[j] = ic2

                # Update response
                r2 = r1 + self.nc[j]
                self.resp[r1:r2] = np.flip(self.resp[r1:r2], 0)
                if self.resp_der:
                    self.dresp[r1:r2] = np.flip(self.dresp[r1:r2], 0)
                r1 = r2

            n1 = n2 + 1

    # -----------------------------------------------------
    # Function to check the response arrays
    # -----------------------------------------------------

    def check(self):
        """Perform a number of checks to see if the response information is consistent."""
        # Check if the number of indexed channels is equal to the length of the response array
        if sum(self.nc) != len(self.resp):
            print("Error: Number of indexed channels not equal to response array.")
            return -1

        # Check if the channel start and end bin are consistent with the number of channels      
        for j in np.arange(len(self.neg)):
            check = self.ic2[j] - self.ic1[j] + 1
            if check != self.nc[j]:
                print("Error: Number of group channels not consistent.")
                return -1

        return 0

    # -----------------------------------------------------
    # Function to create a masks for a certain region
    # -----------------------------------------------------

    def get_mask(self, iregion):
        """Create masks to select a particular region in a .res file. """
        # Check if iregion is in an allowed range
        if (iregion >= self.nregion) and (iregion < 1):
            print("Error: Requested region not available.")
            return -1

        # Find which rows in SPEX_RESP_ICOMP are to be masked
        icomp_sel_rows = np.where(self.region == iregion)[0]
        icomp_front_rows = np.where(self.region < iregion)[0]

        # Find which rows in SPEX_RESP_GROUP are to be masked
        # Make sure the +1 is there in the row selection, because otherwise one row too little is selected.
        if icomp_front_rows.size == 0:
            group_first_row = 0
        else:
            group_first_row = sum(self.neg[np.amin(icomp_front_rows):np.amax(icomp_front_rows) + 1])

        group_last_row = group_first_row + sum(self.neg[np.amin(icomp_sel_rows):np.amax(icomp_sel_rows) + 1])

        # Find which rows in SPEX_RESP_RESP are to be masked
        if group_first_row == 0:
            resp_first_row = 0
        else:
            resp_first_row = sum(self.nc[0:group_first_row])
        resp_last_row = resp_first_row + sum(self.nc[group_first_row:group_last_row])

        # Select region in SPEX_RESP_RESP
        self.mask_resp = np.full(len(self.resp), False, dtype=bool)
        self.mask_resp[resp_first_row:resp_last_row] = True

        # Select region in SPEX_RESP_GROUP
        self.mask_group = np.full(len(self.eg1), False, dtype=bool)
        self.mask_group[group_first_row:group_last_row] = True

        # Select region in SPEX_RESP_ICOMP
        self.mask_icomp = np.full(len(self.neg), False, dtype=bool)
        for i in icomp_sel_rows:
            self.mask_icomp[i] = True

        return 0

    # -----------------------------------------------------
    # Show summary of response file
    # -----------------------------------------------------

    def show(self, iregion=1):
        """Show some basic properties of the response file."""

        tres = self.return_region(iregion)

        print(" Original response file name            :  {0}".format(tres.resname))
        print(" Number of data channels in response    :  {0}".format(tres.nchan[0]))
        print(" Number of response components          :  {0}".format(tres.ncomp))


# =========================================================
# Finally, a trick to run the module from the command line
# as an executable for testing purposes.
# =========================================================

if __name__ == "__main__":
    test = Res()
    test.read_file("rgs.res")
    test.del_res_region(1)
    test.write_file("rgs_test.res")
