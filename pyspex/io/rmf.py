#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import pyspex.messages as message
import numpy as np
import astropy.io.fits as fits
from pyspex.io.arf import Arf

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

        self.Order = 0                #: Order of the matrix

    def read(self,rmffile):
        """Class to read OGIP RMF files. The variable naming is made consistent with the HEASOFT HEASP module by
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

        data = rmf['MATRIX'].data
        header = rmf['MATRIX'].header

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

        fgroup = 0
        felem = 0
        k=0

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

                    k = k + 1

                self.Matrix = np.append(self.Matrix, matrix_local[i])

        self.NumberTotalElements = self.Matrix.size
        self.ResponseThreshold = np.amin(self.Matrix)

        rmf.close()

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

        if not isinstance(arf,Arf):
            message.error("Input arf is not an Arf class instance.")
            return 1

        if arf.LowEnergy.size != self.LowEnergy.size:
            message.error("Size of ARF and RMF are not the same.")
            return 1

        if arf.LowEnergy[0] != self.LowEnergy[0]:
            message.error("Lower Energies of arrays are not the same.")
            return 1

        size = arf.HighEnergy.size - 1

        if arf.HighEnergy[size] != self.HighEnergy[size]:
            message.error("Lower Energies of arrays are not the same.")
            return 1

        return 0