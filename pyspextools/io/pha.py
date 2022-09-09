#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

import pyspextools.messages as message
import numpy as np
import math
import astropy.io.fits as fits
from .rmf import Rmf


class Pha:
    """Class to read OGIP PHA files. The variable naming is made consistent with the HEASOFT HEASP module by
    Keith Arnaud.    
  
    :ivar FirstChannel: First valid spectral channel.
    :vartype FirstChannel: int
    :ivar DetChans: Total number of legal channels.
    :vartype DetChans: int

    :ivar Channel: Spectrum channels.
    :vartype Channel: numpy.ndarray
    :ivar Rate: Spectrum spectrum count rate.
    :vartype Rate: numpy.ndarray
    :ivar StatError: Spectrum error rate (if exists).
    :vartype StatError: numpy.ndarray
    :ivar SysError: Spectrum systematic error.
    :vartype SysError: numpy.ndarray

    :ivar Quality: Quality flag.
    :vartype Quality: numpy.ndarray
    :ivar Grouping: Grouping information.
    :vartype Grouping: numpy.ndarray

    :ivar AreaScaling: Areascal keyword/array.
    :vartype AreaScaling: numpy.ndarray
    :ivar BackScaling: Backscal keyword/array.
    :vartype BackScaling: numpy.ndarray
    :ivar CorrScal: Correction spectrum scaling.
    :vartype CorrScal: float

    :ivar Exposure: Exposure time of the spectrum.
    :vartype Exposure: float
    :ivar Poisserr: Are the errors Poissonian.
    :vartype Poisserr: bool
    :ivar Spectrumtype: Spectrumtype (TOTAL, NET or BKG).
    :vartype SpectrumType: str
    :ivar PhaType: Whether the spectrum is in COUNTS or RATE.
    :vartype PhaType: str

    :ivar rmffile: Associated Response matrix file.
    :vartype rmffile: str
    :ivar arffile: Associated Effective area file.
    :vartype arffile: str
    :ivar bkgfile: Associated Background file.
    :vartype bkgfile: str
    :ivar corfile: Associated Correction spectrum file.
    :vartype corfile: str

    :ivar Pha2Back: Is there a PHA2 background available?
    :vartype Pha2Back: bool
    :ivar BackRate: PHA2 Background Rate.
    :vartype BackRate: numpy.ndarray
    :ivar BackStatError: PHA2 Background Error.
    :vartype BackStatError: numpy.ndarray
    :ivar Pha2BackScal: Backscale value for background.
    :vartype Pha2BackScal: float
    """

    def __init__(self):
        # Spectrum arrays
        self.FirstChannel = 0                       # First valid spectral channel
        self.DetChans = 0                           # Total number of legal channels

        self.Channel = np.array([], dtype=int)      # Spectrum channels
        self.Rate = np.array([], dtype=float)       # Spectrum spectrum count rate
        self.StatError = np.array([], dtype=float)  # Spectrum error rate (if exists)
        self.SysError = np.array([], dtype=float)   # Spectrum systematic error

        self.Quality = np.array([], dtype=int)      # Quality flag
        self.Grouping = np.array([], dtype=int)     # Grouping information

        self.AreaScaling = np.array([], dtype=float)  # Areascal keyword/array
        self.BackScaling = np.array([], dtype=float)  # Backscal keyword/array
        self.CorrScal = 1.0                         # Correction spectrum scaling

        self.Exposure = 0.0                         # Exposure time of the spectrum
        self.Poisserr = True                        # Are the errors Poissonian
        self.Spectrumtype = 'TOTAL'                 # Spectrumtype (TOTAL, NET or BKG)
        self.PhaType = 'COUNTS'                     # Whether the spectrum is in COUNTS or RATE

        self.rmffile = None                         # Associated Response matrix file
        self.arffile = None                         # Associated Effective area file
        self.bkgfile = None                         # Associated Background file
        self.corfile = None                         # Associated Correction spectrum file

        # Only applicable for PHA2 files:
        self.Pha2Back = False                           # Is there a PHA2 background available
        self.BackRate = np.array([], dtype=float)       # PHA2 Background Rate
        self.BackStatError = np.array([], dtype=float)  # PHA2 Background Error
        self.Pha2BackScal = 1.0                         # Backscale value for background

    def read(self, filename):
        """Read a spectrum from a PHA file.

        :param filename: PHA file name to be read.
        :type filename: str
        """

        # Read the data and header from the SPECTRUM extension
        (data, header) = fits.getdata(filename, 'SPECTRUM', header=True)

        # Read the number of channels (outside the header call because of PHAII files).
        self.DetChans = header['DETCHANS']

        # Read the header
        self.read_header(header)

        # Read Channel information
        self.Channel = data['CHANNEL']
        self.FirstChannel = self.Channel[0]

        # Read the spectrum and convert to rate if necessary
        if self.PhaType == 'RATE':
            self.Rate = data['RATE']
        else:
            self.Rate = np.zeros(self.DetChans, dtype=float)
            for i in np.arange(self.DetChans):
                self.Rate[i] = float(data['COUNTS'][i]) / self.Exposure

        # See if there are Statistical Errors present
        if not self.Poisserr:
            try:
                self.StatError = data['STAT_ERR']
            except KeyError:
                self.StatError = None
                message.warning("No Poisson errors, but no STAT_ERR keyword found.")
        else:
            self.StatError = np.zeros(self.DetChans, dtype=float)
            for i in np.arange(self.DetChans):
                self.StatError[i] = math.sqrt(self.Rate[i] / self.Exposure)

        # Are there systematic errors?
        try:
            self.SysError = data['SYS_ERR']
        except KeyError:
            self.SysError = np.zeros(self.DetChans, dtype=float)

        if self.PhaType == 'RATE':
            self.SysError = self.SysError / self.Exposure

        # Are there quality flags?
        try:
            self.Quality = data['QUALITY']
        except KeyError:
            self.Quality = np.zeros(self.DetChans, dtype=int)

        # Are there grouping flags?
        try:
            self.Grouping = data['GROUPING']
        except KeyError:
            self.Grouping = np.zeros(self.DetChans, dtype=int)

        # Is there a backscale column?
        try:
            self.BackScaling = data['BACKSCAL']
        except KeyError:
            self.BackScaling = np.ones(self.DetChans, dtype=float) * header['BACKSCAL']

        # Is there an areascale column?
        try:
            self.AreaScaling = data['AREASCAL']
        except KeyError:
            self.AreaScaling = np.ones(self.DetChans, dtype=float) * header['AREASCAL']

        return 0

    def read_header(self, header):
        """Utility function to read the header from a SPECTRUM extension for both PHA and PHAII files.

        :param header: Header of the SPECTRUM extension.
        :type header: astropy.io.fits.Header
        """

        # Read Exposure information
        self.Exposure = header['EXPOSURE']

        # Read how the spectrum is stored (COUNTS or RATE)
        try:
            self.Spectrumtype = header['HDUCLAS2']
        except KeyError:
            self.Spectrumtype = 'TOTAL'
            message.warning("HDUCLAS2 keyword not found. Assuming spectrumtype is TOTAL.")

        try:
            self.PhaType = header['HDUCLAS3']
        except KeyError:
            self.PhaType = 'COUNTS'
            message.warning("HDUCLAS3 keyword not found. Assuming PHA type is COUNTS.")

        # Read the POISERR keyword
        try:
            self.Poisserr = header['POISSERR']
        except KeyError:
            self.Poisserr = False

        # Read Correction scaling factor
        self.CorrScal = header['CORRSCAL']

        # Read a background file, if available
        try:
            self.bkgfile = header['BACKFILE']
        except KeyError:
            self.bkgfile = None

        # Read an respoonse file, if available
        try:
            self.rmffile = header['RESPFILE']
        except KeyError:
            self.rmffile = None

        # Read an effective area file, if available
        try:
            self.arffile = header['ANCRFILE']
        except KeyError:
            self.arffile = None

        # Read a correction file, if available
        try:
            self.corfile = header['CORRFILE']
        except KeyError:
            self.corfile = None

    def check(self):
        """Check if the object contains the minimum required data."""
        # Check exposure value
        if self.Exposure <= 0.0:
            message.error("Exposure time of spectrum is zero or smaller.")
            return 1
        if self.DetChans <= 0:
            message.error("Number of channels is zero.")
            return 1
        if self.Rate.size <= 0:
            message.error("Size of rate array is zero.")
            return 1

        return 0

    def create_dummy(self, resp):
        """Generate dummy spectrum based on rmf channel information.

        :param resp: Input RMF response object.
        :type resp: pyspextools.io.rmf.Rmf
        """

        if not isinstance(resp, Rmf):
            message.error("Input response object is not the required Rmf object.")
            return

        # First copy the channel information to the PHA object
        self.Channel = resp.ebounds.Channel
        self.FirstChannel = resp.ebounds.Channel[0]
        self.DetChans = resp.ebounds.NumberChannels
    
        # Generate a dummy spectrum (obviously not realistic, should be simulated in SPEX later)
        # Set exposure, statistic and type of spectrum
        self.Exposure = 1000.0
        self.Poisserr = True
        self.Spectrumtype = 'TOTAL'
    
        # Generate spectrum values and quality flags
        self.Rate = np.ones(self.DetChans, dtype=float) / self.Exposure
        self.StatError = np.ones(self.DetChans, dtype=float) / self.Exposure
        self.SysError = np.zeros(self.DetChans, dtype=float)
        self.Quality = np.zeros(self.DetChans, dtype=float)
        self.Grouping = np.zeros(self.DetChans, dtype=float)
        self.AreaScaling = np.ones(self.DetChans, dtype=float)
        self.BackScaling = np.ones(self.DetChans, dtype=float)

    def disp(self):
        """Display a summary of the PHA file."""
        print("")
        print("FirstChannel  {0}  First valid spectral channel".format(self.FirstChannel))
        print("DetChans      {0}  Total number of legal channels".format(self.DetChans))
        print("Exposure      {0}  Exposure time of the spectrum".format(self.Exposure))
        print("Poisserr      {0}  Are the errors Poissonian".format(self.Poisserr))
        print("Spectrumtype  {0}  Spectrumtype (TOTAL, NET or BKG)".format(self.Spectrumtype))
        print("PhaType       {0}  Whether the spectrum is in COUNTS or RATE".format(self.PhaType))
        print("AreaScaling   {0}  Areascal keyword/array".format(self.AreaScaling))
        print("BackScaling   {0}  Backscal keyword/array".format(self.BackScaling))
        print("CorrScal      {0}  Correction spectrum scaling".format(self.CorrScal))
        print("")
        print("Arrays:")
        print("Channel       {0}  Spectrum channels".format(self.Channel.size))
        print("Rate          {0}  Spectrum spectrum count rate".format(self.Rate.size))
        print("StatError     {0}  Spectrum error rate (if exists)".format(self.StatError.size))
        print("SysError      {0}  Spectrum systematic error".format(self.SysError.size))
        print("Quality       {0}  Quality flag".format(self.Quality.size))
        print("Grouping      {0}  Grouping information".format(self.Grouping.size))
        print("")
        print("Associated files:")
        print("rmffile       {0}  Associated Response matrix file".format(self.rmffile))
        print("arffile       {0}  Associated Effective area file".format(self.arffile))
        print("bkgfile       {0}  Associated Background file".format(self.bkgfile))
        print("corfile       {0}  Associated Correction spectrum file".format(self.corfile))
        print("")

    def check_compatibility(self, pha):
        """Check if another PHA object is compatible with the current one in terms of number of channels.

        :param pha: PHA object to check compatibility for.
        :type pha: pyspextools.io.pha.Pha
        """

        # Check equal number of channels
        if self.DetChans != pha.DetChans:
            message.error("Number of channels not equal for both PHA files.")
            return 1

        return 0

    def number_channels(self):
        return self.DetChans
