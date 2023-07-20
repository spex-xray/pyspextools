import pytest
import numpy as np
from pyspextools.io.pha2 import Pha2


class TestPha2:
    """
    Class Analysis

    Main functionalities:
    The Pha2 class is designed to read PHA2 type OGIP spectra. It can read a type II pha file, combine the orders for
    spectra from the same grating, and provide information about the spectra such as the number of spectra, list of
    PHA spectra, array of order numbers, array of grating numbers, instrument name, telescope name, and grating name.

    Methods:
    - read(phafile, force_poisson=True, background=False): reads a type II pha file and sets the values of the fields
      accordingly. It takes the name of the type II PHA file, a flag to set the enforcement of Poisson errors, and a
      flag to subtract the background as input.
    - combine_orders(grating): combines the orders for spectra from the same grating (1 = HETG, 2 = METG, 3 = LETG).
      It takes the grating number to combine the orders for as input.

    Fields:
    - NumberSpectra: Number of spectra in PHAII file.
    - phalist: List of PHA spectra.
    - tg_m: Array of order numbers.
    - tg_part: Array of grating numbers.
    - instrument: Instrument name.
    - telescope: Telescope name.
    - grating: Grating name
    - gratings: Dictionary of grating names.
    """

    def test_read_valid_letg(self):
        """Tests that a valid LETG PHA2 file can be read."""
        pha2 = Pha2()
        pha2.read('data/letg.pha2', force_poisson=False)
        assert pha2.NumberSpectra == 2
        assert pha2.instrument == 'HRC'
        assert pha2.telescope == 'CHANDRA'
        assert pha2.grating == 'LETG'
        assert pha2.phalist[0].PhaType == 'COUNT'
        assert pha2.phalist[0].Rate[0] == 0.0
        assert pytest.approx(pha2.phalist[0].StatError[0]) == 1.8660254
        assert pytest.approx(pha2.phalist[0].SysError[0]) == 0.0
        assert pha2.phalist[0].Quality[0] == 0
        assert pha2.phalist[0].Grouping[0] == 0
        assert pha2.phalist[0].BackScaling[0] == 1.0
        assert pha2.phalist[0].AreaScaling[0] == 1.0

    def test_read_valid_letg_background(self):
        """Tests that a valid LETG PHA2 background file can be read."""
        pha2 = Pha2()
        pha2.read('data/letg.pha2', force_poisson=False, background=True)
        assert pha2.NumberSpectra == 2
        assert pha2.instrument == 'HRC'
        assert pha2.telescope == 'CHANDRA'
        assert pha2.grating == 'LETG'
        assert pha2.phalist[0].PhaType == 'COUNT'
        assert pha2.phalist[0].Rate[0] == 0.0
        assert pytest.approx(pha2.phalist[0].StatError[0]) == 1.8660254
        assert pytest.approx(pha2.phalist[0].SysError[0]) == 0.0
        assert pha2.phalist[0].Quality[0] == 0
        assert pha2.phalist[0].Grouping[0] == 0
        assert pha2.phalist[0].BackScaling[0] == 1.0
        assert pha2.phalist[0].AreaScaling[0] == 1.0
        assert pha2.phalist[0].Pha2Back is True
        assert pytest.approx(pha2.phalist[0].BackRate[0]) == 0.0
        assert pytest.approx(pha2.phalist[0].BackStatError[0]) == 0.0
        assert pytest.approx(pha2.phalist[0].Pha2BackScal) == 10.0

    def test_read_valid_hetg(self):
        """Tests that a valid HETG PHA2 file can be read."""
        pha2 = Pha2()
        pha2.read('data/hetg.pha2', force_poisson=True)
        assert pha2.NumberSpectra == 12
        assert pha2.instrument == 'ACIS'
        assert pha2.telescope == 'CHANDRA'
        assert pha2.grating == 'HETG'
        assert pha2.phalist[0].PhaType == 'COUNT'
        assert pytest.approx(pha2.phalist[0].Rate[0]) == 0.0
        assert pytest.approx(pha2.phalist[0].StatError[0]) == 0.0
        assert pytest.approx(pha2.phalist[0].SysError[0]) == 0.0
        assert pha2.phalist[0].Quality[0] == 0
        assert pha2.phalist[0].Grouping[0] == 0
        assert pha2.phalist[0].BackScaling[0] == 1.0
        assert pha2.phalist[0].AreaScaling[0] == 1.0

    #  Tests that an error is raised when combining orders for an invalid grating
    def test_combine_orders_invalid_grating(self):
        pha2 = Pha2()
        pha2.read('data/hetg.pha2')
        with pytest.raises(ValueError):
            pha2.combine_orders(4)

