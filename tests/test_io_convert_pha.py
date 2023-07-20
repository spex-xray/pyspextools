import pytest

import numpy as np
from pyspextools.io.pha import Pha
from pyspextools.io.rmf import Rmf
from pyspextools.io.arf import Arf
from pyspextools.io.convert import pha_to_spo


class TestPhaToSpo:
    """
    Code Analysis

    Objective:
    - The objective of the 'pha_to_spo' function is to convert OGIP format spectra (source, background, and correction) to SPEX format using an OGIP RMF response matrix object. The function also provides an option to save the grouping information in the PHA file to the SPO file.

    Inputs:
    - 'src': Input PHA source spectrum object.
    - 'rmf': Input RMF response matrix object.
    - 'back': Input PHA background spectrum object (optional).
    - 'corr': Input PHA correction spectrum object (optional).
    - 'save_grouping': Save the group information (True/False).

    Flow:
    - Check if background and correction spectra are provided.
    - Create an empty Spo object.
    - Determine the number of channels and add to Spo.
    - Loop through all the bins for the relevant spectral arrays.
    - Calculate the source rates and errors.
    - Subtract background if available.
    - Subtract correction spectrum, if available.
    - Set background to zero for zero exposure bins.
    - Set first, last, and used variables.
    - Get channel boundaries from response.
    - Check if channel order needs to be swapped.
    - Return Spo object.

    Outputs:
    - Spo object containing the source and background rates.

    Additional aspects:
    - The function checks the consistency of the input arf object with the RMF file.
    - The function issues a warning if the energy units in the response file are not in keV.
    """

    def test_valid_input_values(self):
        """Tests with valid input values for src and rmf objects."""
        src = Pha()
        src.DetChans = 10
        src.Exposure = 1000
        src.AreaScaling = np.ones(10)
        src.Rate = np.ones(10) * 1e-3
        src.StatError = np.ones(10) * 1e-4
        src.Quality = np.zeros(10)
        src.Grouping = np.zeros(10)
        rmf = Rmf()
        rmf.ebounds.NumberChannels = src.DetChans
        rmf.ebounds.ChannelLowEnergy = np.ones(10)
        rmf.ebounds.ChannelHighEnergy = np.ones(10) * 2
        rmf.ebounds.EnergyUnits = 'keV'
        spo = pha_to_spo(src, rmf)
        assert spo.nchan[0] == 10
        assert spo.tints[0] == 1000
        assert np.allclose(spo.ochan, np.ones(10) * 1e-3)
        assert np.allclose(spo.dochan, np.ones(10) * 1e-4)
        assert np.allclose(spo.echan1, np.ones(10))
        assert np.allclose(spo.echan2, np.ones(10) * 2)

    def test_valid_input_values_with_back_and_corr(self):
        """Tests with valid input values for src, rmf, back and corr objects."""
        src = Pha()
        src.DetChans = 10
        src.Exposure = 10000
        src.AreaScaling = np.ones(10)
        src.BackScaling = np.ones(10)
        src.Rate = np.ones(10)
        src.StatError = np.sqrt(src.Rate * src.Exposure) / src.Exposure
        src.Quality = np.zeros(10)
        src.Grouping = np.zeros(10)
        back = Pha()
        back.DetChans = 10
        back.Exposure = 10000
        back.AreaScaling = np.ones(10)
        back.BackScaling = np.ones(10)
        back.Rate = np.ones(10) * 0.01
        back.StatError = np.sqrt(back.Rate * back.Exposure) / back.Exposure
        back.Quality = np.zeros(10)
        back.Grouping = np.zeros(10)
        corr = Pha()
        corr.DetChans = 10
        corr.Exposure = 10000
        corr.AreaScaling = np.ones(10)
        corr.BackScaling = np.ones(10)
        corr.Rate = np.ones(10) * 0.01
        corr.StatError = np.sqrt(corr.Rate * corr.Exposure) / corr.Exposure
        corr.Quality = np.zeros(10)
        corr.Grouping = np.zeros(10)
        rmf = Rmf()
        rmf.ebounds.NumberChannels = src.DetChans
        rmf.ebounds.ChannelLowEnergy = np.ones(src.DetChans)
        rmf.ebounds.ChannelHighEnergy = np.ones(src.DetChans) * 2
        rmf.ebounds.EnergyUnits = 'keV'
        spo = pha_to_spo(src, rmf, back, corr)
        assert spo.nchan[0] == src.DetChans
        assert spo.tints[0] == src.Exposure
        assert np.allclose(spo.ochan, src.Rate - back.Rate - corr.Rate)
        assert np.allclose(spo.dochan, np.sqrt(src.StatError**2 + back.StatError**2 + corr.StatError**2))
        assert np.allclose(spo.echan1, np.ones(10))
        assert np.allclose(spo.echan2, np.ones(10) * 2)

    def test_save_grouping_true(self):
        """Tests with save_grouping flag as True."""
        src = Pha()
        src.DetChans = 10
        src.Exposure = 1000
        src.AreaScaling = np.ones(10)
        src.Rate = np.ones(10) * 1e-3
        src.StatError = np.ones(10) * 1e-4
        src.Quality = np.zeros(10)
        src.Grouping = np.ones(10)
        src.Grouping[1] = -1
        src.Grouping[3] = -1
        src.Grouping[5] = -1
        rmf = Rmf()
        rmf.ebounds.NumberChannels = src.DetChans
        rmf.ebounds.ChannelLowEnergy = np.ones(10)
        rmf.ebounds.ChannelHighEnergy = np.ones(10) * 2
        rmf.ebounds.EnergyUnits = 'keV'
        spo = pha_to_spo(src, rmf, save_grouping=True)
        assert spo.last[0] == False
        assert spo.first[1] == False
        assert spo.last[4] == False
        assert spo.first[5] == False
        assert spo.last[8] == True

    def test_save_grouping_false(self):
        """Tests with save_grouping flag as False."""
        src = Pha()
        src.DetChans = 10
        src.Exposure = 1000
        src.AreaScaling = np.ones(10)
        src.Rate = np.ones(10) * 1e-3
        src.StatError = np.ones(10) * 1e-4
        src.Quality = np.zeros(10)
        src.Grouping = np.zeros(10)
        src.Grouping[0] = 1
        src.Grouping[5] = -1
        rmf = Rmf()
        rmf.ebounds.NumberChannels = src.DetChans
        rmf.ebounds.ChannelLowEnergy = np.ones(10)
        rmf.ebounds.ChannelHighEnergy = np.ones(10) * 2
        rmf.ebounds.EnergyUnits = 'keV'
        spo = pha_to_spo(src, rmf, save_grouping=False)
        assert spo.first[0] == True
        assert spo.last[4] == True
        assert spo.last[5] == True
        assert spo.first[6] == True
        assert spo.last[9] == True

    def test_wrong_src_object(self):
        """Test with wrong src object."""
        src = Arf()
        rmf = Rmf()
        with pytest.raises(AttributeError):
            pha_to_spo(src, rmf)

    def test_empty_src_object(self):
        """Tests with empty src object."""
        src = Pha()
        rmf = Rmf()
        with pytest.raises(AttributeError):
            pha_to_spo(src, rmf)
