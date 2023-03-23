#!/usr/bin/env python

import pyspextools.messages as message
import numpy as np
import astropy.io.fits as fits
from pyspextools.io.arf import Arf


class RmfEbounds:
    """Class to read the EBOUNDS extension from an RMF or RSP file.

    :ivar FirstChannel: First channel number.
    :vartype FirstChannel: int
    :ivar Channel: Channel numbers.
    :vartype Channel: numpy.ndarray
    :ivar ChannelLowEnergy: Start energy of channel.
    :vartype ChannelLowEnergy: numpy.ndarray
    :ivar ChannelHighEnergy: End energy of channel.
    :vartype ChannelHighEnergy: numpy.ndarray
    :ivar NumberChannels: Number of data channels.
    :vartype NumberChannels: int
    :ivar EnergyUnits: Unit of the energy scale
    :vartype EnergyUnits: string
    """

    def __init__(self):
        self.FirstChannel = 0                               # First channel number
        self.Channel = np.array([], dtype=int)              # Channel numbers
        self.ChannelLowEnergy = np.array([], dtype=float)   # Start energy of channel
        self.ChannelHighEnergy = np.array([], dtype=float)  # End energy of channel
        self.NumberChannels = 0                             # Number of data channels
        self.EnergyUnits = ''                               # Unit of the energy scale

    def read(self, rmffile):
        # Read the Ebounds table
        (data, header) = fits.getdata(rmffile, 'EBOUNDS', header=True)

        self.Channel = data['CHANNEL']
        self.ChannelLowEnergy = data['E_MIN']
        self.ChannelHighEnergy = data['E_MAX']
        self.NumberChannels = self.Channel.size
        self.FirstChannel = self.Channel[0]

        try:
            self.EnergyUnits = header['TUNIT2']
        except KeyError:
            message.warning("Could not find energy units in the Energy column. Assuming unit keV")
            self.EnergyUnits = 'keV'


class RmfMatrix:
    """Class to read a MATRIX extension from an OGIP RMF or RSP file.

    :ivar NumberGroups: Number of response groups.
    :vartype NumberGroups: numpy.ndarray
    :ivar FirstGroup: First response group for this energy bin.
    :vartype FirstGroup: numpy.ndarray
    :ivar FirstChannelGroup: First channel number in this group.
    :vartype FirstChannelGroup: numpy.ndarray
    :ivar NumberChannelsGroup: Number of channels in this group.
    :vartype NumberChannelsGroup: numpy.ndarray
    :ivar FirstElement: First response element for this group.
    :vartype FirstElement: numpy.ndarray
    :ivar LowEnergy: Start energy of bin.
    :vartype LowEnergy: numpy.ndarray
    :ivar HighEnergy: End energy of bin.
    :vartype HighEnergy: numpy.ndarray
    :ivar Matrix: Response matrix elements.
    :vartype Matrix: numpy.ndarray

    :ivar NumberEnergyBins: Number of energy bins.
    :vartype NumberEnergyBins: int
    :ivar NumberTotalGroups: Total number of groups.
    :vartype NumberTotalGroups: int
    :ivar NumberTotalElements: Total number of response elements.
    :vartype NumberTotalElements: int

    :ivar AreaScaling: Value of EFFAREA keyword.
    :vartype AreaScaling: float
    :ivar ResponseThreshold: Minimum value in response.
    :vartype ResponseThreshold: float
    :ivar EnergyUnits: Units of the energy scale.
    :vartype EnergyUnits: str
    :ivar RMFUnits: Units for RMF values.
    :vartype RMFUnits: str
    :ivar AreaIncluded: Is the effective area included in the response?
    :vartype AreaIncluded: bool

    :ivar Order: Order of the matrix.
    :vartype Order: int
    """

    def __init__(self):
        self.NumberGroups = np.array([], dtype=int)         # Number of response groups
        self.FirstGroup = np.array([], dtype=int)           # First response group for this energy bin
        self.FirstChannelGroup = np.array([], dtype=int)    # First channel number in this group
        self.NumberChannelsGroup = np.array([], dtype=int)  # Number of channels in this group
        self.FirstElement = np.array([], dtype=int)         # First response element for this group
        self.LowEnergy = np.array([], dtype=float)          # Start energy of bin
        self.HighEnergy = np.array([], dtype=float)         # End energy of bin
        self.Matrix = np.array([], dtype=float)             # Matrix elements

        self.NumberEnergyBins = 0                           # Number of energy bins
        self.NumberTotalGroups = 0                          # Total number of groups
        self.NumberTotalElements = 0                        # Total number of response elements

        self.AreaScaling = 1.0                              # Value of EFFAREA keyword
        self.ResponseThreshold = 1E-7                       # Minimum value in response
        self.EnergyUnits = ''                               # Units of the energy scale
        self.RMFUnits = ''                                  # Units for RMF values
        self.AreaIncluded = False                           # Is the effective area included in the response?

        self.Order = 0                                      # Order of the matrix

    def read(self, rmfhdu):

        # Read the Matrix table
        data = rmfhdu.data
        header = rmfhdu.header

        if rmfhdu.name == 'MATRIX':
            pass
        elif rmfhdu.name == 'SPECRESP MATRIX':
            message.warning("This is an RSP file with the effective area included.")
            print("Do not read an ARF file, unless you know what you are doing.")
            self.AreaIncluded = True
        else:
            message.error("MATRIX extension not successfully found in RMF file.")
            return

        self.LowEnergy = data['ENERG_LO']
        self.HighEnergy = data['ENERG_HI']
        self.NumberEnergyBins = self.LowEnergy.size

        try:
            self.EnergyUnits = header['TUNIT1']
        except KeyError:
            message.warning("Could not find units in the file for the Energy grid. Assuming keV.")
            self.EnergyUnits = 'keV'

        self.NumberGroups = data['N_GRP']
        self.NumberTotalGroups = np.sum(self.NumberGroups)

        self.FirstGroup = np.zeros(self.NumberEnergyBins, dtype=int)

        self.FirstChannelGroup = np.zeros(self.NumberTotalGroups, dtype=int)
        self.NumberChannelsGroup = np.zeros(self.NumberTotalGroups, dtype=int)
        self.FirstElement = np.zeros(self.NumberTotalGroups, dtype=int)

        self.Matrix = np.array([], dtype=float)

        try:
            self.Order = header['ORDER']
        except KeyError:
            pass

        fgroup = 0  # Count total number of groups
        felem = 0   # Count total number of response elements
        nelem = np.zeros(self.NumberEnergyBins, dtype=int)   # Count number of response elements per energy bin
        k = 0

        fchan_local = data['F_CHAN']
        nchan_local = data['N_CHAN']
        matrix_local = data['MATRIX']

        for i in np.arange(self.NumberEnergyBins):
            self.FirstGroup[i] = fgroup
            fgroup = fgroup + self.NumberGroups[i]

            if self.NumberGroups[i] != 0:
                for j in np.arange(self.NumberGroups[i]):
                    try:
                        self.FirstChannelGroup[k] = fchan_local[i][j]
                        self.NumberChannelsGroup[k] = nchan_local[i][j]
                    except IndexError:
                        self.FirstChannelGroup[k] = fchan_local[i]
                        self.NumberChannelsGroup[k] = nchan_local[i]
                    self.FirstElement[k] = felem
                    felem = felem + self.NumberChannelsGroup[k]
                    nelem[i] = nelem[i] + self.NumberChannelsGroup[k]

                    k = k + 1

        self.Matrix = np.zeros(felem, dtype=float)

        r = 0
        for i in np.arange(self.NumberEnergyBins):
            if nelem[i] != 0:
                for j in np.arange(nelem[i]):
                    self.Matrix[r] = matrix_local[i][j]
                    r = r + 1

        self.NumberTotalElements = self.Matrix.size
        self.ResponseThreshold = np.amin(self.Matrix)


class Rmf:
    """Class to read OGIP RMF files. The response is given in two parts: an EBOUNDS extension, containing
    the energy boundries of the instrument channels, and one or more MATRIX extensions, which contain components
    of the response matrix.

    :ivar ebounds: Represents the EBOUNDS extension in the RMF file, which contains the channel energy scale.
    :vartype ebounds: pyspextools.io.rmf.RmfEbounds
    :ivar matrix: List containing the matrix extensions (type pyspextools.io.rmf.RmfMatrix)
    :vartype matrix: list
    :ivar NumberMatrixExt: The number of matrix extensions.
    :vartype NumberMatrixExt: int
    :ivar MatrixExt: Array containing the FITS extension numbers that contain a response matrix.
    :vartype MatrixExt: numpy.ndarray
    """

    def __init__(self):
        self.ebounds = RmfEbounds()
        self.matrix = []
        self.NumberMatrixExt = 0
        self.MatrixExt = np.array([], dtype=int)

    def read(self, rmffile):
        """Method to read OGIP RMF files. The variable naming is made consistent with the HEASOFT HEASP module by
        Keith Arnaud.

        :param rmffile: RMF file name to read.
        :type rmffile: str
        """

        # Read the Ebounds table
        self.ebounds.read(rmffile)

        # Empty lists for safety
        self.NumberMatrixExt = 0
        self.MatrixExt = np.array([], dtype=int)
        self.matrix = []

        # Read the number of MATRIX extensions
        rmf = fits.open(rmffile)
        for i in range(len(rmf)):
            if rmf[i].name == 'MATRIX' or rmf[i].name == 'SPECRESP MATRIX':
                self.NumberMatrixExt += 1
                self.MatrixExt = np.append(self.MatrixExt, i)

        # Read the individual matrix extensions
        for i in self.MatrixExt:
            mat = RmfMatrix()
            mat.read(rmf[i])
            self.matrix.append(mat)

        rmf.close()

        return 0

    def write(self, rmffile, telescop=None, instrume=None, filterkey=None, overwrite=False):
        """Method to write an OGIP format RMF file.

        :param rmffile: RMF file name to write.
        :type rmffile: str
        :param telescop: Name of the telescope to be put in the TELESCOP keyword.
        :type telescop: str
        :param instrume: Name of the instrument to be put in the INSTRUME keyword.
        :type instrume: str
        :param filterkey: Name of the filter to be put in the FILTER keyword.
        :type filterkey: str
        :param overwrite: Overwrite existing file names? (True/False)
        :type overwrite: bool
        """

        #
        # Generate warning if there are multiple groups per energy
        #
        if np.amax(self.matrix[0].NumberGroups) != 1:
            message.warning("This method has not been tested for responses with multiple response groups per energy.")

        #
        # Create Primary HDU
        #
        primary = fits.PrimaryHDU()

        #
        # Create the EBOUNDS extension
        #
        ecol1 = fits.Column(name='CHANNEL', format='J', array=self.ebounds.Channel)
        ecol2 = fits.Column(name='E_MIN', format='D', unit=self.ebounds.EnergyUnits, array=self.ebounds.ChannelLowEnergy)
        ecol3 = fits.Column(name='E_MAX', format='D', unit=self.ebounds.EnergyUnits, array=self.ebounds.ChannelHighEnergy)

        ebnds = fits.BinTableHDU.from_columns([ecol1, ecol2, ecol3])

        ehdr = ebnds.header
        ehdr.set('EXTNAME', 'EBOUNDS')
        ehdr.set('DETCHANS', self.ebounds.NumberChannels)

        # Set the TELESCOP keyword (optional)
        if telescop is None:
            ehdr.set('TELESCOP', 'None', 'Telescope name')
        else:
            ehdr.set('TELESCOP', telescop, 'Telescope name')

        # Set the INSTRUME keyword (optional)
        if instrume is None:
            ehdr.set('INSTRUME', 'None', 'Instrument name')
        else:
            ehdr.set('INSTRUME', instrume, 'Instrument name')

        # Set the FILTER keyword (optional)
        if filterkey is None:
            ehdr.set('FILTER', 'None', 'Filter setting')
        else:
            ehdr.set('FILTER', filterkey, 'Filter setting')

        ehdr.set('DETNAM ', 'None')
        ehdr.set('CHANTYPE', 'PI')
        ehdr.set('HDUCLASS', 'OGIP')
        ehdr.set('HDUCLAS1', 'RESPONSE')
        ehdr.set('HDUCLAS2', 'EBOUNDS ')
        ehdr.set('HDUVERS1', '1.2.0')
        ehdr.set('ORIGIN ', 'SRON')

        hdu = fits.HDUList([primary, ebnds])

        #
        # Create SPECRESP MATRIX extension
        #
        for e in range(self.NumberMatrixExt):
            print("Writing matrix for matrix number: {0}".format(e))

            mcol1 = fits.Column(name='ENERG_LO', format='D', unit=self.matrix[e].EnergyUnits, array=self.matrix[e].LowEnergy)
            mcol2 = fits.Column(name='ENERG_HI', format='D', unit=self.matrix[e].EnergyUnits, array=self.matrix[e].HighEnergy)
            mcol3 = fits.Column(name='N_GRP', format='J', array=self.matrix[e].NumberGroups)
            mcol4 = fits.Column(name='F_CHAN', format='J', array=self.matrix[e].FirstChannelGroup)
            mcol5 = fits.Column(name='N_CHAN', format='J', array=self.matrix[e].NumberChannelsGroup)

            # Determine the width of the matrix
            width = np.amax(self.matrix[e].NumberChannelsGroup)
            formatstr = str(width)+'D'

            #
            # THIS PART COULD BE UPDATED TO OPTIMIZE THE SIZE USING VARIABLE SIZE ARRAYS IN FITS.
            #

            # Building the MATRIX column
            newmatrix = np.zeros(self.matrix[e].NumberEnergyBins * width, dtype=float).reshape(self.matrix[e].NumberEnergyBins, width)

            re = 0
            for i in np.arange(self.matrix[e].NumberEnergyBins):
                for j in np.arange(self.matrix[e].NumberGroups[i]):
                    for k in np.arange(self.matrix[e].NumberChannelsGroup[i]):
                        newmatrix[i, k] = self.matrix[e].Matrix[re]
                        re = re + 1

            mcol6 = fits.Column(name='MATRIX', format=formatstr, array=newmatrix)

            matrix = fits.BinTableHDU.from_columns([mcol1, mcol2, mcol3, mcol4, mcol5, mcol6])

            mhdr = matrix.header

            if self.matrix[e].AreaIncluded:
                mhdr.set('EXTNAME', 'SPECRESP MATRIX')
            else:
                mhdr.set('EXTNAME', 'MATRIX')

            # Set the TELESCOP keyword (optional)
            if telescop is None:
                mhdr.set('TELESCOP', 'None', 'Telescope name')
            else:
                mhdr.set('TELESCOP', telescop, 'Telescope name')

            # Set the INSTRUME keyword (optional)
            if instrume is None:
                mhdr.set('INSTRUME', 'None', 'Instrument name')
            else:
                mhdr.set('INSTRUME', instrume, 'Instrument name')

            # Set the FILTER keyword (optional)
            if filterkey is None:
                mhdr.set('FILTER', 'None', 'Filter setting')
            else:
                mhdr.set('FILTER', filterkey, 'Filter setting')

            mhdr.set('DETCHANS', self.ebounds.NumberChannels)
            mhdr.set('LO_THRES', self.matrix[e].ResponseThreshold)

            mhdr.set('CHANTYPE', 'PI')
            mhdr.set('HDUCLASS', 'OGIP')
            mhdr.set('HDUCLAS1', 'RESPONSE')
            mhdr.set('HDUCLAS2', 'RSP_MATRIX')

            if self.matrix[e].AreaIncluded:
                mhdr.set('HDUCLAS3', 'FULL')
            else:
                mhdr.set('HDUCLAS3', 'REDIST')
            mhdr.set('HDUVERS1', '1.3.0')
            mhdr.set('ORIGIN  ', 'SRON')

            matrix.header['HISTORY'] = 'Created by pyspextools:'
            matrix.header['HISTORY'] = 'https://github.com/spex-xray/pyspextools'

            hdu.append(matrix)

        try:
            hdu.writeto(rmffile, overwrite=overwrite)
        except IOError:
            message.error("File {0} already exists. I will not overwrite it!".format(rmffile))
            return 1

        return 0

    def check(self):
        """Check the RMF for internal consistency."""
        if self.ebounds.NumberChannels <= 0:
            message.error("Number of Channels in response is zero.")
            return 1

        for e in range(self.NumberMatrixExt):
            if self.matrix[e].NumberEnergyBins <= 0:
                message.error("Number of Energy bins in response is zero.")
                return 1

            c = 0
            r = 0
            # Check if matrix array is consistent with the indexing
            for i in np.arange(self.matrix[e].NumberEnergyBins):
                for j in np.arange(self.matrix[e].NumberGroups[i]):
                    for k in np.arange(self.matrix[e].NumberChannelsGroup[c]):
                        r = r + 1
                    c = c + 1

            if r != self.matrix[e].Matrix.size:
                message.error("Matrix size does not correspond to index arrays. Response inconsistent.")
                return 1

        return 0

    def disp(self):
        """Display a summary of the RMF object."""
        print("RMF Response matrix:")
        print("")
        print("Channel energy bounds:")
        print("FirstChannel:        {0:>20}  First channel number".format(self.ebounds.FirstChannel))
        print("NumberChannels:      {0:>20}  Number of data channels".format(self.ebounds.NumberChannels))
        print("Channel              {0:>20}  Channel numbers".format(self.ebounds.Channel.size))
        print("ChannelLowEnergy     {0:>20}  Start energy of channel".format(self.ebounds.ChannelLowEnergy.size))
        print("ChannelHighEnergy    {0:>20}  End energy of channel".format(self.ebounds.ChannelHighEnergy.size))
        print("")
        print("NumberMatrixExt      {0:>10}  Number of MATRIX extensions".format(self.NumberMatrixExt))
        for i in range(self.NumberMatrixExt):
            print("")
            print("Information for MATRIX number {0}:".format(i+1))
            print("NumberEnergyBins:    {0:>20}  Number of energy bins".format(self.matrix[i].NumberEnergyBins))
            print("NumberTotalGroups:   {0:>20}  Total number of groups".format(self.matrix[i].NumberTotalGroups))
            print("NumberTotalElements: {0:>20}  Total number of response elements".format(self.matrix[i].NumberTotalElements))
            print("AreaScaling          {0:>20}  Value of EFFAREA keyword".format(self.matrix[i].AreaScaling))
            print("ResponseThreshold    {0:>20g}  Minimum value in response".format(self.matrix[i].ResponseThreshold))
            print("EnergyUnits          {0:>20}  Units of the energy scale".format(self.matrix[i].EnergyUnits))
            print("RMFUnits             {0:>20}  Units for RMF values".format(self.matrix[i].RMFUnits))
            print("")
            print("NumberGroups         {0:>20}  Number of response groups".format(self.matrix[i].NumberGroups.size))
            print("FirstGroup           {0:>20}  First response group for this energy bin".format(self.matrix[i].FirstGroup.size))
            print("FirstChannelGroup    {0:>20}  First channel number in this group".format(self.matrix[i].FirstChannelGroup.size))
            print("NumberChannelsGroup  {0:>20}  Number of channels in this group".format(self.matrix[i].NumberChannelsGroup.size))
            print("FirstElement         {0:>20}  First response element for this group".format(self.matrix[i].FirstElement.size))
            print("LowEnergy            {0:>20}  Start energy of bin".format(self.matrix[i].LowEnergy.size))
            print("HighEnergy           {0:>20}  End energy of bin".format(self.matrix[i].HighEnergy.size))
            print("Matrix               {0:>20}  Matrix elements".format(self.matrix[i].Matrix.size))
            print("")

        return

    def check_compatibility(self, arf):
        """Check whether the input arf object is really an ARF object with data and consistent with this RMF file.

        :param arf: Input arf object to check.
        :type arf: pyspextools.io.Arf
        """

        # Check if arf is really an Arf object
        if not isinstance(arf, Arf):
            message.error("Input arf is not an Arf class instance.")
            return 1

        # Check if the size of the energy arrays is the same.
        if arf.LowEnergy.size != self.matrix[0].LowEnergy.size:
            message.error("Size of ARF and RMF are not the same.")
            return 1

        # Check if the numbers of the high energy column are the same
        # Here we check the high values, because sometimes the first low value is different...
        if arf.HighEnergy[0] != self.matrix[0].HighEnergy[0]:
            message.error("First high-energy boundaries of arrays are not the same.")
            return 1

        # Check if the last values of the array are similar.
        size = arf.HighEnergy.size - 1

        if arf.HighEnergy[size] != self.matrix[0].HighEnergy[size]:
            message.error("Last high-energy boundaries of arrays are not the same.")
            return 1

        return 0
