#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
from scipy.signal import savgol_filter, wiener
from astropy.convolution import convolve_fft, Gaussian1DKernel
import pyspextools.messages as message

# Stuff to import for compatibility between python 2 and 3
from builtins import int

from future import standard_library

standard_library.install_aliases()


class Filter:
    """Class to smooth background spectra (EXPERIMENTAL).

    :ivar nchan: Number of data channels.
    :vartype nchan: int
    :ivar channel: Array containing data channels.
    :vartype channel: np.ndarray
    :ivar original: Array containing the original spectrum.
    :vartype original: np.ndarray
    :ivar filtered: Array containing the filtered spectrum.
    :vartype filtered: np.ndarray

    :ivar method: Which method to use?
    :vartype method: str
    """

    def __init__(self):
        self.nchan = 0
        self.channel = np.array([])
        self.original = np.array([])
        self.error = np.array([])
        self.filtered = np.array([])
        self.instrument = None
        self.chanmin = np.array([])
        self.chanmax = np.array([])

    def read_pha(self, pha):
        """Read the background spectrum from a Pha object.

        :param pha: OGIP PHA object to read the background from.
        :type pha: pyspextools.io.ogip.Pha
        """
        self.nchan = pha.DetChans
        self.channel = pha.Channel
        self.original = pha.Rate
        self.error = pha.StatError
        self.filtered = np.zeros(self.nchan, dtype=float)
        self.instrument = pha.Instrument

        self.chanmin = np.array([0])
        self.chanmax = np.array([self.nchan])

        # Detect CCD boundaries for RGS
        if self.instrument == 'RGS1' or self.instrument == 'RGS2':
            self.chanmin = np.zeros(18, dtype=int)
            self.chanmax = self.nchan * np.ones(18, dtype=int)
            ccd = -1
            ingap = True
            for i in np.arange(self.nchan):
                if pha.Quality[i] == 1 and pha.AreaScaling[i] == 1.0:
                    if not ingap:
                        self.chanmax[ccd] = i - 1
                        ingap = True
                else:
                    if ingap:
                        ccd = ccd + 1
                        self.chanmin[ccd] = i
                        ingap = False

            self.chanmin = self.chanmin[0:ccd+1]
            self.chanmax = self.chanmax[0:ccd+1]

    def read_spo(self, spo, iregion=1):
        """Read the background spectrum from a spo file.

        :param spo: SPEX spo object to read the background from.
        :type spo: pyspextools.io.Spo
        :param iregion: Region number to extract background spectrum from.
        :type iregion: int
        """
        regspo = spo.return_region(iregion)
        self.nchan = regspo.nchan[0]
        self.channel = regspo.echan1
        self.original = regspo.mbchan
        self.filtered = np.zeros(self.nchan, dtype=float)

    def savgol(self, window_length, polyorder):
        """Apply a Savitzky-Golay filter to the spectrum. See the `savgol_filter
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
        documentation of Scipy for more information.

        :param window_length: The length of the filter window (i.e. the number of coefficients).
        window_length must be a positive odd integer.
        :type window_length: int
        :param polyorder: The order of the polynomial used to fit the samples.
        polyorder must be less than window_length.
        :type polyorder: int
        """

        if self.nchan == 0:
            message.error("No spectrum loaded. Please load a spectrum.")
            return

        for i in np.arange(self.chanmin.size):
            try:
                self.filtered[self.chanmin[i]:self.chanmax[i]] = savgol_filter(self.original[self.chanmin[i]:self.chanmax[i]], window_length, polyorder)
            except ValueError:
                message.error("The window length (first number) needs to be a positive odd integer and \n"
                              "the polyorder (second number) needs to be an integer smaller than the window length.")

    def wiener(self, mysize, noise=None):
        """Apply a Wiener filter to the spectrum. See the `wiener
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.wiener.html>`_
        documentation of Scipy for more information.

        :param mysize: A scalar giving the size of the Wiener filter window in one dimension.
        :type mysize: int
        :param noise: The noise-power to use. If None, then noise is estimated as the average of the local variance of the input.
        :type noise: int
        """

        if self.nchan == 0:
            message.error("No spectrum loaded. Please load a spectrum.")
            return

        for i in np.arange(self.chanmin.size):
            try:
                self.filtered[self.chanmin[i]:self.chanmax[i]] = wiener(self.original[self.chanmin[i]:self.chanmax[i]], mysize, noise=noise)
            except ValueError:
                message.error("Input filter window size and noise should be integer.")

    def gauss(self, stddev):
        """Apply a Gaussian convolution to the spectrum.

        :param stddev: Standard deviation of the Gaussian kernel to apply.
        :type stddev: int
        """
        if self.nchan == 0:
            message.error("No spectrum loaded. Please load a spectrum.")
            return

        for i in np.arange(self.chanmin.size):
            try:
                gaussfunc = Gaussian1DKernel(stddev=stddev)
                data_ave = np.mean(self.original[self.chanmin[i]:self.chanmax[i]])
                self.filtered[self.chanmin[i]:self.chanmax[i]] = convolve_fft(self.original[self.chanmin[i]:self.chanmax[i]], gaussfunc, boundary='fill', fill_value=data_ave, normalize_kernel=True)
            except:
                message.error("Please provide a positive standard deviation.")

    def write_pha(self, pha, filename):
        """Write a simple PHA file"""

        pha.Rate = self.filtered
        pha.StatError = pha.StatError * 0.
        pha.Poisserr = False
        pha.PhaType = 'RATE'
        pha.write(filename)
