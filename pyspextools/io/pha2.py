#!/usr/bin/env python

import pyspextools.messages as message
import numpy as np
import math
import astropy.io.fits as fits

from .pha import Pha


class Pha2:
    """ Class to read PHA2 type OGIP spectra.

    :ivar NumberSpectra: Number of spectra in PHAII file.
    :vartype NumberSpectra: int
    :ivar phalist: List of PHA spectra.
    :vartype phalist: list
    :ivar tg_m: Array of order numbers.
    :vartype tg_m: numpy.ndarray
    :ivar tg_part: Array of grating numbers.
    :vartype tg_part: numpy.ndarray
    :ivar instrument: Instrument name.
    :vartype instrument: str
    :ivar telescope: Telescope name.
    :vartype telescope: str
    :ivar grating: Grating name
    :vartype grating: str

    :ivar gratings: Dictionary of grating names.
    :vartype gratings: dict
    """

    def __init__(self):
        self.NumberSpectra = 0                  # Number of spectra in PHAII file
        self.phalist = []                       # List of PHA spectra
        self.tg_m = np.array([])                # Array of order numbers
        self.tg_part = np.array([])             # Array of grating numbers
        self.instrument = ''                    # Instrument name
        self.telescope = ''                     # Telescope name
        self.grating = ''                       # Grating name

        self.gratings = {'1': 'heg', '2': 'meg', '3': 'leg'}

    def read(self, phafile, force_poisson=True, background=False):
        """Read a type II pha file. Many time Gehrels errors are provided, but we prefer Poisson. Therefore, the
        optional 'force_poisson' flag is True by default. Set force_poisson to false to obtain the errors from
        the file. If the user wants to subtract the background, the flag 'background' should be set to True.

        :param phafile: Name of the type II PHA file.
        :type phafile: str
        :param force_poisson: Flag to set the enforcement of Poisson errors.
        :type force_poisson: bool
        :param background: Subtract the background (True/False)?
        :type background: bool
        """

        file = fits.open(phafile)
        header = file['SPECTRUM'].header
        data = file['SPECTRUM'].data

        self.NumberSpectra = header['NAXIS2']
        self.tg_m = data['TG_M']
        self.tg_part = data['TG_PART']
        self.instrument = header['INSTRUME']
        self.telescope = header['TELESCOP']
        self.grating = header['GRATING']

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
                    pha.Rate[j] = float(data['COUNTS'][i][j]) / pha.Exposure

            if force_poisson:
                poisson = True
            else:
                poisson = pha.Poisserr

            # See if there are Statistical Errors present
            if not poisson:
                try:
                    pha.StatError = data['STAT_ERR'][i]
                except KeyError:
                    pha.StatError = None
                    message.error("No Poisson errors, but no STAT_ERR keyword found.")
                    return 1
            else:
                pha.StatError = np.zeros(pha.DetChans, dtype=float)
                for j in np.arange(pha.DetChans):
                    pha.StatError[j] = math.sqrt(pha.Rate[j] / pha.Exposure)

            # Are there systematic errors?
            try:
                pha.SysError = data['SYS_ERR'][i]
            except KeyError:
                pha.SysError = np.zeros(pha.DetChans, dtype=float)

            if pha.PhaType == 'RATE':
                pha.SysError = pha.SysError / pha.Exposure

            # Are there quality flags?
            try:
                pha.Quality = data['QUALITY'][i]
            except KeyError:
                pha.Quality = np.zeros(pha.DetChans, dtype=int)

            # Are there grouping flags?
            try:
                pha.Grouping = data['GROUPING'][i]
            except KeyError:
                pha.Grouping = np.zeros(pha.DetChans, dtype=int)

            # Is there a backscale column?
            try:
                pha.BackScaling = data['BACKSCAL'][i]
            except KeyError:
                pha.BackScaling = np.ones(pha.DetChans, dtype=float) * header['BACKSCAL']

            # Is there an areascale column?
            try:
                pha.AreaScaling = data['AREASCAL'][i]
            except KeyError:
                pha.AreaScaling = np.ones(pha.DetChans, dtype=float) * header['AREASCAL']

            if background:
                pha.Pha2Back = True
                pha.BackRate = (data['BACKGROUND_UP'][i] + data['BACKGROUND_DOWN'][i]) / pha.Exposure
                pha.BackStatError = np.zeros(data['BACKGROUND_UP'].size, dtype=float)
                for j in np.arange(pha.DetChans):
                    pha.BackStatError[j] = math.sqrt(pha.BackRate[j] / pha.Exposure)
                pha.Pha2BackScal = header['BACKSCUP'] + header['BACKSCDN']
            else:
                pha.Pha2Back = False
                pha.BackRate = np.zeros(pha.DetChans, dtype=float)
                pha.BackStatError = np.zeros(pha.DetChans, dtype=float)
                pha.Pha2BackScal = 1.0

            self.phalist.append(pha)

        file.close()
        return 0

    def combine_orders(self, grating):
        """Combine the orders for spectra from the same grating (1 = HETG, 2 = METG, 3 = LETG).

        :param grating: Grating number to combine the orders for.
        :type grating: int
        """

        # Select rows to combine
        tocombine = np.where(self.tg_part == grating)[0]

        if tocombine.size == 0:
            message.error("Grating number not found in dataset.")
            return 1

        if tocombine.size == 1:
            message.error("Only a single order found. No combining will be done.")
            return 1

        # Create new PHA file to output (set first row as default).
        srcpha = self.phalist[tocombine[0]]
        bkgpha = Pha()
        bkgpha.StatError = np.zeros(srcpha.DetChans, dtype=float)

        for i in np.arange(tocombine.size):
            if i == 0:
                continue

            ipha = self.phalist[tocombine[i]]

            srcpha.Rate = srcpha.Rate + ipha.Rate
            bkgpha.Rate = srcpha.BackRate + ipha.BackRate

            for j in np.arange(srcpha.DetChans):
                if srcpha.StatError is not None:
                    srcpha.StatError[j] = math.sqrt(srcpha.StatError[j]**2 + ipha.StatError[j]**2)
                    bkgpha.StatError[j] = math.sqrt(srcpha.BackStatError[j]**2 + ipha.BackStatError[j]**2)
                srcpha.SysError[j] = math.sqrt(srcpha.SysError[j]**2 + ipha.SysError[j]**2)
                if ipha.Quality[j] != 0:
                    srcpha.Quality = 1

            # Remove grouping for now (maybe implemented later)
            srcpha.Grouping = 0 * srcpha.Grouping

            srcpha.AreaScaling = srcpha.AreaScaling + ipha.AreaScaling
            srcpha.BackScaling = srcpha.BackScaling + ipha.BackScaling

        # Calculate the average AreaScaling and BackScaling (Probably wrong!)
        srcpha.AreaScaling = srcpha.AreaScaling / tocombine.size
        srcpha.BackScaling = srcpha.BackScaling / tocombine.size

        bkgpha.AreaScaling = np.ones(srcpha.DetChans, dtype=float)
        bkgpha.BackScaling = srcpha.Pha2BackScal * np.ones(srcpha.DetChans, dtype=float)
        bkgpha.Quality = np.zeros(srcpha.DetChans, dtype=int)
        bkgpha.Exposure = srcpha.Exposure

        return srcpha, bkgpha
