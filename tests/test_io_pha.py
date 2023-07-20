import pytest
from pyspextools.io.pha import Pha
import numpy as np

"""
Code Analysis

Main functionalities:
The Pha class is designed to handle X-ray spectral data in the form of PHA (Pulse Height Amplitude) files. It can read in PHA files, extract relevant information from the header and data, and store this information in various arrays. It can also create dummy PHA files based on a given response matrix file, and check for compatibility between two PHA files.

Methods:
- read(filename): reads in a PHA file and extracts relevant information from the header and data, storing it in various arrays.
- read_header(header): extracts relevant information from the header and stores it in various fields.
- check(): checks for errors in the PHA file, such as zero exposure time or zero number of channels.
- create_dummy(resp): creates a dummy PHA file based on a given response matrix file.
- disp(): displays the relevant information stored in the PHA object.
- check_compatibility(pha): checks for compatibility between two PHA files based on their number of channels.
- number_channels(): returns the number of channels in the PHA file.

Fields:
- FirstChannel: the first valid spectral channel.
- DetChans: the total number of legal channels.
- Channel: an array of spectrum channels.
- Rate: an array of spectrum count rates.
- StatError: an array of error rates (if they exist).
- SysError: an array of systematic errors.
- Quality: an array of quality flags.
- Grouping: an array of grouping information.
- AreaScaling: an array of areascal keywords/arrays.
- BackScaling: an array of backscal keywords/arrays.
- CorrScal: the correction spectrum scaling.
- Exposure: the exposure time of the spectrum.
- Poisserr: a boolean indicating whether the errors are Poissonian.
- Spectrumtype: the spectrum type (TOTAL, NET or BKG).
- PhaType: whether the spectrum is in COUNTS or RATE.
- rmffile: the associated response matrix file.
- arffile: the associated effective area file.
- bkgfile: the associated background file.
- corfile: the associated correction spectrum file.
- Pha2Back: a boolean indicating whether the PHA file is a background file.
- BackRate: an array of background count rates.
- BackStatError: an array of background error rates (if they exist).
- Pha2BackScal: the PHA to background scaling factor.
"""


class TestPha:

    def test_init_default_values(self):
        """Tests that a new instance of Pha initializes all attributes to their default values."""
        pha = Pha()
        assert pha.FirstChannel == 0
        assert pha.DetChans == 0
        assert np.array_equal(pha.Channel, np.array([], dtype=int))
        assert np.array_equal(pha.Rate, np.array([], dtype=float))
        assert np.array_equal(pha.StatError, np.array([], dtype=float))
        assert np.array_equal(pha.SysError, np.array([], dtype=float))
        assert np.array_equal(pha.Quality, np.array([], dtype=int))
        assert np.array_equal(pha.Grouping, np.array([], dtype=int))
        assert np.array_equal(pha.AreaScaling, np.array([], dtype=float))
        assert np.array_equal(pha.BackScaling, np.array([], dtype=float))
        assert pha.CorrScal == 1.0
        assert pha.Exposure == 0.0
        assert pha.Poisserr == True
        assert pha.Spectrumtype == 'TOTAL'
        assert pha.PhaType == 'COUNTS'
        assert pha.rmffile == None
        assert pha.arffile == None
        assert pha.bkgfile == None
        assert pha.corfile == None
        assert pha.Pha2Back == False
        assert np.array_equal(pha.BackRate, np.array([], dtype=float))
        assert np.array_equal(pha.BackStatError, np.array([], dtype=float))
        assert pha.Pha2BackScal == 1.0

#    def test_read_valid_file(self):
#        """Tests that calling read() method with a valid filename reads the data from the file and populates the
#        attributes of the object."""
#        pha = Pha()
#        pha.read('data/pha_valid.pha')
#        assert pha.DetChans == 10
#        assert pha.FirstChannel == 0
#        assert np.array_equal(pha.Channel, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
#        assert np.array_equal(pha.Rate, np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]))
#        assert np.array_equal(pha.StatError, np.array([1.0, 1.41421356, 1.73205081, 2.0, 2.23606798, 2.44948974, 2.64575131, 2.82842712, 3.0, 3.16227766]))
#        assert np.array_equal(pha.SysError, np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]))
#        assert np.array_equal(pha.Quality, np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
#        assert np.array_equal(pha.Grouping, np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
#        assert np.array_equal(pha.AreaScaling, np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]))
#        assert np.array_equal(pha.BackScaling, np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]))
#        assert pha.CorrScal == 2.0
#        assert pha.Exposure == 1000.0
#        assert pha.Poisserr == True
#        assert pha.Spectrumtype == 'TOTAL'
#        assert pha.PhaType == 'COUNTS'
#        assert pha.rmffile == 'rmf_file.fits'
#        assert pha.arffile == 'arf_file.fits'
#        assert pha.bkgfile == 'bkg_file.fits'
#        assert pha.corfile == 'cor_file.fits'
#        assert pha.Pha2Back == False
#        assert np.array_equal(pha.BackRate, np.array([], dtype=float))
#        assert np.array_equal(pha.BackStatError, np.array([], dtype=float))
#        assert pha.Pha2BackScal == 1.0

    def test_read_nonexistent_file(self):
        """Tests that calling read() method with a non-existent filename raises an error."""
        pha = Pha()
        with pytest.raises(FileNotFoundError):
            pha.read('data/pha_nonexistent_file.pha')

    def test_check_exposure_time_zero(self):
        """Tests that calling check() method with an Exposure time of zero returns 1."""
        pha = Pha()
        pha.Exposure = 0.0
        assert pha.check() == 1

    def test_check_number_channels_zero(self):
        """Tests that calling check() method with a number of channels of zero returns 1"""
        pha = Pha()
        pha.DetChans = 0
        assert pha.check() == 1

    def test_create_dummy_invalid_Rmf_object(self):
        """Tests that calling create_dummy() method with an invalid Rmf object raises an error"""
        pha = Pha()
        resp = 'invalid_Rmf_object'
        with pytest.raises(AttributeError):
            pha.create_dummy(resp)
