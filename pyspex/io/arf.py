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

standard_library.install_aliases()

class Arf:
    """Class to read OGIP ARF files. The variable naming is made consistent with the HEASOFT HEASP module by
    Keith Arnaud."""

    def __init__(self):
        self.LowEnergy = np.array([],dtype=float)      #: Low Energy of bin
        self.HighEnergy = np.array([],dtype=float)     #: High Energy of bin
        self.EffArea = np.array([],dtype=float)        #: Effective Area of bin

        self.EnergyUnits = 'keV'                       #: Energy units
        self.arfUnits = 'cm2'
        self.Order = 0                                 #: Grating order (for grating arrays, else 0)
        self.Grating = 0                               #: Grating instrument (if available, 1 = HEG, 2 = MEG, 3 = LEG)

    def read(self,arffile):
        """Read the effective area from an OGIP ARF file."""

        (data, header) = fits.getdata(arffile,'SPECRESP',header=True)

        self.LowEnergy = data['ENERG_LO']
        self.HighEnergy = data['ENERG_HI']
        self.EffArea = data['SPECRESP']

        self.EnergyUnits = header['TUNIT1']

        if header['TUNIT3'] == 'cm**2':
            self.arfUnits = 'cm2'
        elif header['TUNIT3'] == 'cm2':
            self.arfUnits = 'cm2'
        else:
            message.warning("ARF units are not recognized.")

        try:
            self.Order = header['TG_M']
            self.Grating = header['TG_PART']
        except:
            self.Order = 0
            self.Grating = 0

        # Check for NULL values
        nans = np.isnan(self.EffArea)
        if np.any(nans):
            for i in np.arange(self.EffArea.size):
                if nans[i]:
                   self.EffArea[i] = 0.0

        return 0

    def check(self):
        """Check if the basic information is read in."""
        if self.LowEnergy.size <= 0:
            message.error("Energy array has zero length.")
            return 1
        if self.EffArea.size <= 0:
            message.error("Effective area array has zero length.")
            return 1

        return 0

    def disp(self):
        """Display a summary of the ARF object."""
        print("ARF effective area:")
        print("LowEnergy array:   {0}  Low Energy of bin".format(self.LowEnergy.size))
        print("HighEnergy array:  {0}  High Energy of bin".format(self.HighEnergy.size))
        print("EffArea array:     {0}  Effective Area of bin".format(self.EffArea.size))
        print("Energy units:      {0}  Energy units".format(self.EnergyUnits))
        print("Area units:        {0}  Area units".format(self.arfUnits))

        return


