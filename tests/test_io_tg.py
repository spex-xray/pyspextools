import pytest
from pyspextools.io.tg import TGRegion
from pyspextools.io.spo import Spo
from pyspextools.io.res import Res


class TestTGRegion:
    """
    Code Analysis

    Main functionalities:
    The TGRegion class is designed to read Chandra grating data into the pyspextools module and convert it to spo
    and res format objects. It contains methods to add a Chandra spectrum and response to a SPEX region, read a PHA
    type II file, and convert a list of compatible rmf and arf files into one res file.

    Methods:
    - read_region: adds a Chandra spectrum and response to a SPEX region by reading a PHA2 file and rmf and arf file
      lists, and converting the PHA2 file to spo and the responses to res.
    - __read_pha2: reads a PHA type II file for a particular grating, combines spectra from a single grating, and
      returns the source and background spectra.
    - __rmflist_to_res: converts a list of compatible rmf and arf files into one res file by reading the responses
      and effective areas for each order, sorting them, and appending the components to the first response.

    Fields:
    - grating: the name of the grating being read.
    """

    def test_read_region_success(self):
        """Tests that read_region method successfully reads a PHA2 file and converts it to a Spo object and reads a
        list of RMF and ARF files and converts them to a Res object."""
        tg = TGRegion()
        pha2file = 'data/pha2.fits'
        rmflist = ['data/rmf2_-1.fits', 'data/rmf2_1.fits']
        arflist = ['data/arf2_-1.fits', 'data/arf2_1.fits']
        bkgsubtract = True
        grating = 'LETG'
        tg.read_region(pha2file, rmflist, arflist, grating, bkgsubtract)
        assert isinstance(tg.spo, Spo)
        assert isinstance(tg.res, Res)
        assert tg.grating == 'LETG'

    def test_read_region_pha2_failure(self):
        """Tests that read_region method raises a ValueError if the PHA2 file cannot be read."""
        tg = TGRegion()
        pha2file = 'data/nonexistent_file.fits'
        rmflist = ['data/rmf2_-1.fits', 'data/rmf2_1.fits']
        arflist = ['data/arf2_-1.fits', 'data/arf2_1.fits']
        grating = 'LETG'
        bkgsubtract = True
        with pytest.raises(ValueError):
            tg.read_region(pha2file, rmflist, arflist, grating, bkgsubtract)

    def test_read_region_unsupported_grating(self):
        """Tests that read_region method raises a ValueError if the grating name is unsupported."""
        tg = TGRegion()
        pha2file = 'data/pha2.fits'
        rmflist = ['data/rmf2_-1.fits', 'data/rmf2_1.fits']
        arflist = ['data/arf2_-1.fits', 'data/arf2_1.fits']
        grating = 'unsupported_grating'
        bkgsubtract = True
        with pytest.raises(ValueError):
            tg.read_region(pha2file, rmflist, arflist, grating, bkgsubtract)

    def test_read_region_success_attributes(self):
        """Tests that read_region method sets the grating attribute to the provided grating name, subtracts the
        background if bkgsubtract is True, combines spectra from a single grating, and sets the label attribute
        to the provided grating name"""
        TG = TGRegion()
        pha2file = 'data/pha2.fits'
        rmflist = ['data/rmf2_-1.fits', 'data/rmf2_1.fits']
        arflist = ['data/arf2_-1.fits', 'data/arf2_1.fits']
        grating = 'LETG'
        bkgsubtract = True
        TG.read_region(pha2file, rmflist, arflist, grating, bkgsubtract)
        assert TG.grating == grating
        assert isinstance(TG.spo, Spo)
        assert isinstance(TG.res, Res)
        assert TG.label == grating
