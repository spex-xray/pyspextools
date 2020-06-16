#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
from scipy.signal import savgol_filter, wiener
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

        try:
            self.filtered = savgol_filter(self.original, window_length, polyorder)
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

        try:
            self.filtered = wiener(self.original, mysize, noise=noise)
        except ValueError:
            message.error("Input filter window size and noise should be integer.")

    def write_pha(self, pha, filename):
        """Write a simple PHA file"""

        pha.Rate = self.filtered
        pha.StatError = pha.StatError * 0.
        pha.Poisserr = False
        pha.PhaType = 'RATE'
        pha.write(filename)
