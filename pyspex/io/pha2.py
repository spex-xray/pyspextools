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
import math
import astropy.io.fits as fits

from .pha import Pha

standard_library.install_aliases()

class Pha2:

    def __init__(self):
        self.NumberSpectra = 0      #: Number of spectra in PHAII file
        self.phalist = []           #: List of PHA spectra
        self.tg_m = np.array([])    #: Array of order numbers
        self.tg_part = np.array([]) #: Array of grating numbers

    def read(self,phafile):

        file = fits.open(phafile)
        header = file['SPECTRUM'].header
        data = file['SPECTRUM'].data

        self.NumberSpectra = header['NAXIS']
        self.tg_m = data['TG_M']

        for i in np.arange(self.NumberSpectra):
            pha = Pha()

            # Read Channel information

            pha.read_header(header)

            # Read Channel information
            pha.Channel = data['CHANNEL'][i]
            pha.FirstChannel = pha.Channel[0]
            pha.DetChans = pha.Channel.size

            # Read the spectrum and convert to rate if necessary
            if pha.PhaType == 'RATE':
                pha.Rate = data['RATE'][i]
            else:
                pha.Rate = np.zeros(pha.DetChans, dtype=float)
                for j in np.arange(pha.DetChans):
                    pha.Rate[i] = float(data['COUNTS'][i][j]) / pha.Exposure

            # See if there are Statistical Errors present
            if not pha.Poiserr:
                try:
                    pha.StatError = data['STAT_ERR'][i]
                except:
                    pha.StatError = None
                    message.warning("No Poisson errors, but no STAT_ERR keyword found.")
            else:
                pha.StatError = np.zeros(pha.DetChans, dtype=int)
                for j in np.arange(pha.DetChans):
                    pha.StatError[i] = math.sqrt(pha.Rate[i] / pha.Exposure)

            # Are there systematic errors?
            try:
                pha.SysError = data['SYS_ERR'][i]
            except:
                pha.SysError = np.zeros(pha.DetChans, dtype=float)

            if pha.PhaType == 'RATE':
                pha.SysError = pha.SysError / pha.Exposure

            # Are there quality flags?
            try:
                pha.Quality = data['QUALITY'][i]
            except:
                pha.Quality = np.zeros(pha.DetChans, dtype=int)

            # Are there grouping flags?
            try:
                pha.Grouping = data['GROUPING'][i]
            except:
                pha.Grouping = np.zeros(pha.DetChans, dtype=int)

            # Is there a backscale column?
            try:
                pha.BackScaling = data['BACKSCAL'][i]
            except:
                pha.BackScaling = np.ones(pha.DetChans, dtype=float) * header['BACKSCAL']

            # Is there an areascale column?
            try:
                pha.AreaScaling = data['AREASCAL'][i]
            except:
                pha.AreaScaling = np.ones(pha.DetChans, dtype=float) * header['AREASCAL']

            self.phalist.append(pha)

        file.close()

        return 0
