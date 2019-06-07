#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import pyspextools.messages as message
import numpy as np
import astropy.io.fits as fits
from pyspextools.io.arf import Arf

standard_library.install_aliases()


class Rmf:
    """Class to read OGIP RMF files. The variable naming is made consistent with the HEASOFT HEASP module by
    Keith Arnaud."""

    def __init__(self):
        self.FirstChannel = 0                            #: First channel number
        self.Channel = np.array([],dtype=int)            #: Channel numbers
        self.NumberGroups = np.array([], dtype=int)      #: Number of response groups
        self.FirstGroup = np.array([], dtype=int)        #: First response group for this energy bin
        self.FirstChannelGroup = np.array([], dtype=int) #: First channel number in this group
        self.NumberChannelsGroup = np.array([], dtype=int) #: Number of channels in this group
        self.FirstElement = np.array([], dtype=int)      #: First response element for this group
        self.LowEnergy = np.array([], dtype=float)       #: Start energy of bin
        self.HighEnergy = np.array([], dtype=float)      #: End energy of bin
        self.Matrix = np.array([], dtype=float)          #: Matrix elements
        self.ChannelLowEnergy = np.array([], dtype=float) #: Start energy of channel
        self.ChannelHighEnergy = np.array([], dtype=float) #: End energy of channel

        self.NumberChannels = 0                          #: Number of data channels
        self.NumberEnergyBins = 0                        #: Number of energy bins
        self.NumberTotalGroups = 0                       #: Total number of groups
        self.NumberTotalElements = 0                     #: Total number of response elements

        self.AreaScaling = 1.0        #: Value of EFFAREA keyword
        self.ResponseThreshold = 1E-7 #: Minimum value in response
        self.EnergyUnits = ''         #: Units of the energy scale
        self.RMFUnits = ''            #: Units for RMF values
        self.AreaIncluded = False     #: Is the effective area included in the response?

        self.Order = 0                #: Order of the matrix

    def read(self,rmffile):
        """Method to read OGIP RMF files. The variable naming is made consistent with the HEASOFT HEASP module by
        Keith Arnaud."""

        # Read the Ebounds table
        (data, header) = fits.getdata(rmffile, 'EBOUNDS', header=True)

        self.Channel = data['CHANNEL']
        self.ChannelLowEnergy = data['E_MIN']
        self.ChannelHighEnergy = data['E_MAX']
        self.NumberChannels = self.Channel.size
        self.FirstChannel = self.Channel[0]

        # Read the Matrix table
        rmf = fits.open(rmffile)

        try:
            data = rmf['MATRIX'].data
            header = rmf['MATRIX'].header
        except:
            data = rmf['SPECRESP MATRIX'].data
            header = rmf['SPECRESP MATRIX'].header
            message.warning("This is an RSP file with the effective area included.")
            print("Do not read an ARF file, unless you know what you are doing.")
            self.AreaIncluded = True

        self.LowEnergy = data['ENERG_LO']
        self.HighEnergy = data['ENERG_HI']
        self.NumberEnergyBins = self.LowEnergy.size
        self.EnergyUnits = header['TUNIT1']

        self.NumberGroups = data['N_GRP']
        self.NumberTotalGroups = np.sum(self.NumberGroups)

        self.FirstGroup = np.zeros(self.NumberEnergyBins, dtype=int)

        self.FirstChannelGroup = np.zeros(self.NumberTotalGroups, dtype=int)
        self.NumberChannelsGroup = np.zeros(self.NumberTotalGroups, dtype=int)
        self.FirstElement = np.zeros(self.NumberTotalGroups, dtype=int)

        self.Matrix = np.array([],dtype=float)

        try:
            self.Order = header['ORDER']
        except:
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
                    r=r+1


        self.NumberTotalElements = self.Matrix.size
        self.ResponseThreshold = np.amin(self.Matrix)

        rmf.close()

        return 0

    def write(self, rmffile, telescop=None, instrume=None, filter=None, overwrite=False):
        '''Method to write an OGIP format RMF file.'''

        #
        # Generate warning if there are multiple groups per energy
        #
        if (np.amax(self.NumberGroups)!=1):
            message.warning("This method has not been tested for responses with multiple response groups per energy.")

        #
        # Create Primary HDU
        #
        primary = fits.PrimaryHDU()

        #
        # Create the EBOUNDS extension
        #
        ecol1 = fits.Column(name='CHANNEL', format='J', array=self.Channel)
        ecol2 = fits.Column(name='E_MIN', format='D', unit=self.EnergyUnits, array=self.ChannelLowEnergy)
        ecol3 = fits.Column(name='E_MAX', format='D', unit=self.EnergyUnits, array=self.ChannelHighEnergy)

        ebounds = fits.BinTableHDU.from_columns([ecol1, ecol2, ecol3])

        ehdr = ebounds.header
        ehdr.set('EXTNAME','EBOUNDS')
        ehdr.set('DETCHANS',self.NumberChannels)

        # Set the TELESCOP keyword (optional)
        if telescop == None:
            ehdr.set('TELESCOP','None','Telescope name')
        else:
            ehdr.set('TELESCOP',telescop,'Telescope name')

        # Set the INSTRUME keyword (optional)
        if instrume == None:
            ehdr.set('INSTRUME','None','Instrument name')
        else:
            ehdr.set('INSTRUME',instrume,'Instrument name')

        # Set the FILTER keyword (optional)
        if filter == None:
            ehdr.set('FILTER','None','Filter setting')
        else:
            ehdr.set('FILTER',filter,'Filter setting')

        ehdr.set('DETNAM ','None')
        ehdr.set('CHANTYPE','PI')
        ehdr.set('HDUCLASS','OGIP')
        ehdr.set('HDUCLAS1','RESPONSE')
        ehdr.set('HDUCLAS2','EBOUNDS ')
        ehdr.set('HDUVERS1','1.2.0')
        ehdr.set('ORIGIN ','SRON')

        #
        # Create SPECRESP MATRIX extension
        #
        mcol1 = fits.Column(name='ENERG_LO', format='D', unit=self.EnergyUnits, array=self.LowEnergy)
        mcol2 = fits.Column(name='ENERG_HI', format='D', unit=self.EnergyUnits, array=self.HighEnergy)
        mcol3 = fits.Column(name='N_GRP', format='J', array=self.NumberGroups)
        mcol4 = fits.Column(name='F_CHAN', format='J', array=self.FirstChannelGroup)
        mcol5 = fits.Column(name='N_CHAN', format='J', array=self.NumberChannelsGroup)

        # Determine the width of the matrix
        width = np.amax(self.NumberChannelsGroup)
        format = str(width)+'D'

        # Building the MATRIX column
        newmatrix = np.zeros(self.Matrix.size, dtype=float).reshape(self.NumberEnergyBins,width)

        re = 0
        for i in np.arange(self.NumberEnergyBins):
            for j in np.arange(self.NumberGroups[i]):
                for k in np.arange(self.NumberChannelsGroup[i]):
                    newmatrix[i,k] = self.Matrix[re]
                    re = re + 1

        mcol6 = fits.Column(name='MATRIX', format=format, array=newmatrix)

        matrix = fits.BinTableHDU.from_columns([mcol1, mcol2, mcol3, mcol4, mcol5, mcol6])

        mhdr = matrix.header

        if self.AreaIncluded:
            mhdr.set('EXTNAME','SPECRESP MATRIX')
        else:
            mhdr.set('EXTNAME','MATRIX')

        # Set the TELESCOP keyword (optional)
        if telescop == None:
            mhdr.set('TELESCOP','None','Telescope name')
        else:
            mhdr.set('TELESCOP',telescop,'Telescope name')

        # Set the INSTRUME keyword (optional)
        if instrume == None:
            mhdr.set('INSTRUME','None','Instrument name')
        else:
            mhdr.set('INSTRUME',instrume,'Instrument name')

        # Set the FILTER keyword (optional)
        if filter == None:
            mhdr.set('FILTER','None','Filter setting')
        else:
            mhdr.set('FILTER',filter,'Filter setting')

        mhdr.set('DETCHANS',self.NumberChannels)
        mhdr.set('LO_THRES',self.ResponseThreshold)

        mhdr.set('CHANTYPE','PI')
        mhdr.set('HDUCLASS','OGIP')
        mhdr.set('HDUCLAS1','RESPONSE')
        mhdr.set('HDUCLAS2','RSP_MATRIX')

        if self.AreaIncluded:
            mhdr.set('HDUCLAS3','FULL')
        else:
            mhdr.set('HDUCLAS3','REDIST')
        mhdr.set('HDUVERS1','1.3.0')
        mhdr.set('ORIGIN  ','SRON')

        matrix.header['HISTORY'] = 'Created by pyspextools:'
        matrix.header['HISTORY'] = 'https://github.com/spex-xray/pyspextools'

        #
        # Final HDU List
        #
        hdu = fits.HDUList([primary, ebounds, matrix])

        try:
            hdu.writeto(rmffile, overwrite=overwrite)
        except IOError:
            message.error("File {0} already exists. I will not overwrite it!".format(rmffile))
            return 1

        return 0

    def check(self):
        """Check the RMF for internal consistency."""
        if self.NumberChannels <= 0:
            message.error("Number of Channels in response is zero.")
            return 1
        if self.NumberEnergyBins <= 0:
            message.error("Number of Energy bins in response is zero.")
            return 1

        c = 0
        r = 0
        # Check if matrix array is consistent with the indexing
        for i in np.arange(self.NumberEnergyBins):
            for j in np.arange(self.NumberGroups[i]):
                for k in np.arange(self.NumberChannelsGroup[c]):
                    r = r + 1
                c = c + 1

        if r != self.Matrix.size:
            message.error("Matrix size does not correspond to index arrays. Response inconsistent.")
            return 1

        return 0

    def disp(self):
        """Display a summary of the RMF object."""
        print("RMF Response matrix:")
        print("FirstChannel:        {0}  First channel number".format(self.FirstChannel))
        print("NumberChannels:      {0}  Number of data channels".format(self.NumberChannels))
        print("NumberEnergyBins:    {0}  Number of energy bins".format(self.NumberEnergyBins))
        print("NumberTotalGroups:   {0}  Total number of groups".format(self.NumberTotalGroups))
        print("NumberTotalElements: {0}  Total number of response elements".format(self.NumberTotalElements))
        print("AreaScaling          {0}  Value of EFFAREA keyword".format(self.AreaScaling))
        print("ResponseThreshold    {0}  Minimum value in response".format(self.ResponseThreshold))
        print("EnergyUnits          {0}  Units of the energy scale".format(self.EnergyUnits))
        print("RMFUnits             {0}  Units for RMF values".format(self.RMFUnits))
        print("")
        print("Arrays:")
        print("Channel              {0}  Channel numbers".format(self.Channel.size))
        print("ChannelLowEnergy     {0}  Start energy of channel".format(self.ChannelLowEnergy.size))
        print("ChannelHighEnergy    {0}  End energy of channel".format(self.ChannelHighEnergy.size))
        print("NumberGroups         {0}  Number of response groups".format(self.NumberGroups.size))
        print("FirstGroup           {0}  First response group for this energy bin".format(self.FirstGroup.size))
        print("FirstChannelGroup    {0}  First channel number in this group".format(self.FirstChannelGroup.size))
        print("NumberChannelsGroup  {0}  Number of channels in this group".format(self.NumberChannelsGroup.size))
        print("FirstElement         {0}  First response element for this group".format(self.FirstElement.size))
        print("LowEnergy            {0}  Start energy of bin".format(self.LowEnergy.size))
        print("HighEnergy           {0}  End energy of bin".format(self.HighEnergy.size))
        print("Matrix               {0}  Matrix elements".format(self.Matrix.size))
        print("")

        return

    def checkCompatibility(self,arf):

        # Check if arf is really an Arf object
        if not isinstance(arf,Arf):
            message.error("Input arf is not an Arf class instance.")
            return 1

        # Check if the size of the energy arrays is the same.
        if arf.LowEnergy.size != self.LowEnergy.size:
            message.error("Size of ARF and RMF are not the same.")
            return 1

        # Check if the numbers of the high energy column are the same
        # Here we check the high values, because sometimes the first low value is different...
        if arf.HighEnergy[0] != self.HighEnergy[0]:
            message.error("First high-energy boundaries of arrays are not the same.")
            return 1

        # Check if the last values of the array are similar.
        size = arf.HighEnergy.size - 1

        if arf.HighEnergy[size] != self.HighEnergy[size]:
            message.error("Last high-energy boudaries of arrays are not the same.")
            return 1

        return 0