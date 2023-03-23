#!/usr/bin/env python

# =========================================================
"""
  Python module to read and write SPEX res files.
  SPEX res files contain the response matrix and effective area
  See this page for the format specification: 
      
    https://spex-xray.github.io/spex-help/theory/response.html
  
  This file contains the res class
 
  Dependencies:
    - astropy.io.fits:     Read and write FITS files
    - numpy:               Array operations
"""
# =========================================================

import pyspextools.messages as message
import astropy.io.fits as fits
import numpy as np
import datetime
import math
import os


# =========================================================
# The res class contains the response information for one
# res file. This file can contain multiple responses (regions).
# =========================================================

class Res:
    """The res class contains the response information for one
    res file. This file can contain multiple responses (regions).

    :ivar resname: Name of the res file.
    :vartype resname: str
    :ivar empty: Is the object still empty? (True/False)
    :vartype empty: bool

    :ivar nchan: Number of energy channels.
    :vartype nchan: numpy.ndarray
    :ivar neg: Number of energy bins.
    :vartype neg: numpy.ndarray
    :ivar sector: Array containing sector numbers.
    :vartype sector: numpy.ndarray
    :ivar region: Array containing region numbers.
    :vartype region: numpy.ndarray
    :ivar shcomp: Array containing shared components.
    :vartype shcomp: numpy.ndarray

    :ivar nsector: Number of sectors.
    :vartype nsector: int
    :ivar nregion: Number of regions.
    :vartype nregion: int
    :ivar ncom: Number of response components
    :vartype ncom: int

    :ivar share_comp: Are there any shared components?
    :vartype share_comp: bool
    :ivar area_scal: Is there areascal information?
    :vartype area_scal: bool
    :ivar resp_der: Are there response derivatives?
    :vartype resp_der: bool

    :ivar eg1: Start energies for response group.
    :vartype eg1: numpy.ndarray
    :ivar eg2: End energies for response group.
    :vartype eg2: numpy.ndarray
    :ivar ic1: Start channel for response group.
    :vartype ic1: numpy.ndarray
    :ivar ic2: End channel for response group.
    :vartype ic2: numpy.ndarray
    :ivar nc: Number of data channels in the group.
    :vartype nc: numpy.ndarray
    :ivar relarea: Area scaling factors.
    :vartype relarea: numpy.ndarray

    :ivar resp: Response values for group (m**2).
    :vartype resp: numpy.ndarray
    :ivar dresp: Response derivatives for group (optional).
    :vartype dresp: numpy.ndarray

    :ivar mask_resp: Mask array used to select certain response values.
    :vartype mask_resp: numpy.ndarray
    :ivar mask_group: Mask array used to select certain groups.
    :vartype mask_group: numpy.ndarray
    :ivar mask_icomp: Mask array used to select certain components.
    :vartype mask_icomp: numpy.ndarray

    :ivar swap: Should the channel order be swapped?
    :vartype swap: bool
    """

    def __init__(self):
        """Initialize a SPEX response object."""

        self.resname = ''
        self.empty = True

        # Response components (SPEX_RESP_ICOMP)
        self.nchan = np.array([], dtype=int)
        self.neg = np.array([], dtype=int)
        self.sector = np.array([], dtype=int)
        self.region = np.array([], dtype=int)
        self.shcomp = np.array([], dtype=int)

        self.nsector = 0
        self.nregion = 0
        self.ncomp = 0

        self.share_comp = False
        self.area_scal = False
        self.resp_der = False

        # Response groups (SPEX_RESP_GROUP)
        self.eg1 = np.array([], dtype=float)
        self.eg2 = np.array([], dtype=float)
        self.ic1 = np.array([], dtype=int)
        self.ic2 = np.array([], dtype=int)
        self.nc = np.array([], dtype=int)
        self.relarea = np.array([], dtype=float)

        # Response values (SPEX_RESP_RESP)
        self.resp = np.array([], dtype=float)
        self.dresp = np.array([], dtype=float)

        # Mask arrays
        self.mask_resp = np.array([], dtype=bool)
        self.mask_group = np.array([], dtype=bool)
        self.mask_icomp = np.array([], dtype=bool)

        # Should channel order be swapped?
        self.swap = False

    # -----------------------------------------------------
    # Function to add a response from another region
    # -----------------------------------------------------

    def add_res_region(self, origres, isector=1, iregion=1):
        """Function to add region(s) to a response.

        :param origres: Response object to be added to this one.
        :type origres: pyspextools.io.Res
        :param isector: Sector number of the response object to add.
        :type isector: int
        :param iregion: Region number of the response object to add.
        :type iregion: int
        """

        stat = origres.get_mask(isector, iregion)
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

        if self.empty:
            self.empty = False

    # -----------------------------------------------------
    # Function to remove a region from a response
    # -----------------------------------------------------

    def del_res_region(self, isector, iregion):
        """Remove region with number 'iregion'.

        :param isector: Sector number of the region to be removed.
        :type isector: int
        :param iregion: Region number of the region to be removed.
        :type iregion: int
        """

        stat = self.get_mask(isector, iregion)
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
        """Function to read a response from a .res file.

        :param resfile: Response filename to be read.
        :type resfile: str
        """

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

    def return_region(self, isector, iregion):
        """Return a res object with the data from 1 selected region.

        :param isector: Sector number of the region to be returned.
        :type isector: int
        :param iregion: Region number of the region to be returned.
        :type iregion: int
        """

        stat = self.get_mask(isector, iregion)
        if stat != 0:
            print("Error: Cannot select sector and region.")
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
            resreg.dresp = self.dresp[mask]

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

        if self.share_comp:
            resreg.shcomp = self.shcomp[mask]

        resreg.ncomp = len(resreg.region)
        resreg.nsector = 1
        resreg.nregion = 1

        resreg.resname = self.resname

        resreg.empty = False

        # Check the new response
        resreg.check()

        return resreg

    # -----------------------------------------------------
    # Function to write a response to a .res file
    # -----------------------------------------------------

    def write_file(self, resfile, overwrite=False, history=None):
        """Write the response information to a .res file with name 'resfile'.

        :param resfile: Name of the response file to write to.
        :type resfile: str
        :param overwrite: Should we overwrite existing files?
        :type overwrite: bool
        :param history: History information
        :type history: List/Array of strings
        """

        check = self.check()
        if check != 0:
            print("Error: Response check failed.")
            return

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
        col1 = fits.Column(name='Response', format='1D', unit='m**2', array=self.resp)
        if self.resp_der:
            col2 = fits.Column(name='Response_Der', format='1D', unit='m**2', array=self.dresp)
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
            return 1

        return 0

    # -----------------------------------------------------
    # Swap the channel order between wavelength and energy order
    # -----------------------------------------------------

    def swap_order(self):
        """Swap the channel order of the response between wavelength or energy order. This is
        for example helpful for grating spectra, which are originally stored in wavelength order
        but must be flipped to energy order in SPEX format."""

        # Loop over components to swap the channel numbers
        n1 = 0   # Lowest channel number
        r1 = 0   # Index of response array

        for i in np.arange(self.ncomp):
            n2 = n1 + self.neg[i]
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
    # Add component to RES file
    # -----------------------------------------------------
    def append_component(self, addres, iregion=1, isector=1):
        """Append a component to the response matrix from another matrix. This is used to add orders to the response
        file for Chandra grating data.

        :param addres: Response object to extract response information from.
        :type addres: pyspextools.io.Res
        :param iregion: Region number to add to the response.
        :type iregion: int
        :param isector: Sector number to add to the response.
        :type isector: int
        """

        # Append line to SPEX_RESP_ICOMP
        self.nchan = np.append(self.nchan, addres.nchan)
        self.neg = np.append(self.neg, addres.neg)
        self.sector = np.append(self.sector, isector)
        self.region = np.append(self.region, iregion)
        if self.share_comp:
            self.shcomp = np.append(self.shcomp, addres.shcomp)

        self.ncomp = self.ncomp + addres.ncomp

        # Append response groups (SPEX_RESP_ICOMP)
        self.eg1 = np.append(self.eg1, addres.eg1)
        self.eg2 = np.append(self.eg2, addres.eg2)
        self.ic1 = np.append(self.ic1, addres.ic1)
        self.ic2 = np.append(self.ic2, addres.ic2)
        self.nc = np.append(self.nc, addres.nc)
        if self.area_scal:
            self.relarea = np.append(self.relarea, addres.relarea)

        # Append
        self.resp = np.append(self.resp, addres.resp)
        if self.resp_der:
            self.dresp = np.append(self.dresp, addres.dresp)

        return 0

    # -----------------------------------------------------
    # Function to create a masks for a certain region
    # -----------------------------------------------------

    def get_mask(self, isector, iregion):
        """Create masks to select a particular region in a .res file.

        :param isector: Sector number to create mask for.
        :type isector: int
        :param iregion: Region number to create mask for.
        :type iregion: int
        """

        # Check if iregion is in an allowed range
        if (iregion >= self.nregion) and (iregion < 1):
            print("Error: Requested region not available.")
            return -1

        # Check if isector is in an allowed range
        if (isector >= self.nsector) and (iregion < 1):
            print("Error: Requested sector not available.")
            return -1

        # Check if isector and iregion combination is available
        ispectrum = 0
        for i in np.arange(len(self.region)):
            if (self.sector[i] == isector) and (self.region[i] == iregion):
                ispectrum = i + 1
        if ispectrum == 0:
            print("Error: Requested sector and region not available")
            return -1

        # Find which rows in SPEX_RESP_ICOMP are to be masked
        icomp_reg = np.where(self.region == iregion)[0]
        icomp_sec = np.where(self.sector == isector)[0]
        icomp_sel_rows = np.intersect1d(icomp_reg, icomp_sec)

        icomp_front_sec = np.where(self.sector < isector)[0]
        icomp_front_reg = np.where(self.region < iregion)[0]
        icomp_front_rows = np.unique(np.append(icomp_front_reg, icomp_front_sec))

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
    # Shift response array
    # -----------------------------------------------------
    def channel_shift(self, shift):
        """Shift the response array indices with an integer number provided by input parameter 'shift'.

        :param shift: Number of channels to shift the spectrum with.
        :type shift: int
        """

        # Check if input shift is indeed an integer
        if not isinstance(shift, int):
            message.error("Entered shift is not an integer number. Not doing anything")
            return -1

        ic1 = np.zeros(self.eg1.size, dtype=int)
        ic2 = np.zeros(self.eg2.size, dtype=int)

        for i in np.arange(self.eg1.size):
            ic1[i] = self.ic1[i] + shift
            ic2[i] = self.ic2[i] + shift
            if ic2[i] > np.amax(self.nchan):
                message.error("Maximum channel number is larger than actual channel range!")
                print("Aborting shift.")
                return -1

        # Save the shifted channel numbers
        self.ic1 = ic1
        self.ic2 = ic2

        return 0

    # -----------------------------------------------------
    # Function to check the response arrays
    # -----------------------------------------------------

    def check(self):
        """Perform a number of checks to see if the response information is consistent."""
        # Check if the number of indexed channels is equal to the length of the response array
        if sum(self.nc) != self.resp.size:
            print("")
            message.error("Number of indexed channels not equal to response array.")
            print("Sum of channels in group:  {0}".format(sum(self.nc)))
            print("Length of response array:  {0}".format(self.resp.size))
            return -1

        # Check if the channel start and end bin are consistent with the number of channels
        for j in np.arange(len(self.neg)):
            check = self.ic2[j] - self.ic1[j] + 1
            if check != self.nc[j]:
                message.error("Number of group channels not consistent.")
                return -1

        # Check if energy grid is monotonous
        k = 0
        for i in np.arange(self.ncomp):
            for j in np.arange(self.neg[i]):
                if self.eg1[k] >= self.eg2[k]:
                    message.error("Energy bin size is not positive for"
                                  "bin {0} of component {1}.".format(j, i))
                    return -1
                if j > 1:
                    if self.eg1[k] < self.eg1[k-1]:
                        message.error("Energy grid is not increasing for"
                                      "bin {0} of component {1}.".format(j, i))
                        return -1
                if self.nc[k] > 0 and self.ic1[k] < 1:
                    message.error("For row {0} the first channel is {1}, which is not allowed.".format(k, self.ic1[k]))
                    return -1
                elif self.nc[k] > 0 and self.ic2[k] > self.nchan[i]:
                    message.error("For row {0} the last channel is larger than the number of channels.".format(k))
                    return -1
                elif self.ic2[k] < self.ic1[k]:
                    message.error("For row {0} the last channel is smaller than the first channel.".format(k))
                    return -1
                elif self.nc[k] > 0 and self.nc[k] != self.ic2[k] - self.ic1[k] + 1:
                    message.error("For row {0} the number of channels does not match the limits.".format(k))
                    return -1
                k = k + 1

        for i in np.arange(self.resp.size):
            if self.resp[i] < 0.0:
                message.error("Negative response value detected in matrix.")
                return -1

        return 0

    # -----------------------------------------------------
    # Function to check the res file name for correct extension
    # -----------------------------------------------------

    def check_filename(self, filename):
        """Check if the output filename has the correct .res extension. The method returns a correct file name.

        :param filename: File name to check.
        :type filename: str
        """
        resname, res_extension = os.path.splitext(filename)
        if res_extension != ".res":
            message.warning("Output filename does not have the correct .res extension.")
            print("Renaming file to end with '.res'.")
            print("")
            resfile = resname + '.res'
        else:
            resfile = filename

        return resfile

    # -----------------------------------------------------
    # Show summary of response file
    # -----------------------------------------------------

    def show(self, iregion=1, isector=1):
        """Show some basic properties of the response file.

        :param iregion: Region number to show.
        :type iregion: int
        :param isector: Sector number to show.
        :type isector: int
        """

        tres = self.return_region(isector, iregion)

        print(" Original response file name            :  {0}".format(tres.resname))
        print(" Number of data channels in response    :  {0}".format(tres.nchan[0]))
        print(" Number of response components          :  {0}".format(tres.ncomp))
