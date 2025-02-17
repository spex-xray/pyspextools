import pytest
from pyspextools.io.region import Region
from pyspextools.io.spo import Spo
from pyspextools.io.res import Res
import numpy as np


class TestRegion:
    """
    Code Analysis

    Main functionalities:
    The Region class is a combination of the Spo and Res classes, which contain spectral and response information,
    respectively. It allows for the creation of a single object that contains both the spectral and response
    information for a specific observation, instrument, or region on the sky. The class provides methods to set
    and change the label, sector, and region number of the object, as well as to check the compatibility of
    the spectrum and response and to show a summary of the region metadata.

    Methods:
    - __init__: initializes the Spo and Res objects and sets the label field to an empty string
    - change_label: attaches a label to the region object
    - set_sector: sets the sector number for the region object
    - set_region: sets the region number for the region object
    - increase_region: increases the region numbers by a specified amount
    - check: checks the compatibility of the spectrum and response and whether the arrays consist of one region
      (if nregion flag is set)
    - show: shows a summary of the region metadata, including the Spo and Res objects

    Fields:
    - spo: a Spo object containing spectral information
    - res: a Res object containing response information
    - label: an optional label to identify the region object
    """

    def test_create_region_object(self):
        """Tests that a Region object can be created with a Spo and Res object."""
        region = Region()
        assert isinstance(region.spo, Spo)
        assert isinstance(region.res, Res)

    def test_attach_label(self):
        """Tests that a label can be attached to a Region object."""
        region = Region()
        region.change_label('MOS1')
        assert region.label == 'MOS1'

    def test_set_sector_number(self):
        """Tests that the sector number can be set for a Region object."""
        region = Region()
        region.set_sector(2)
        assert np.all(region.res.sector == 2)

    def test_set_region_number(self):
        """Tests that the region number can be set for a Region object."""
        region = Region()
        region.set_region(3)
        assert np.all(region.res.region == 3)

    def test_check_compatibility(self):
        """Tests that the check method correctly identifies incompatible spectrum and response arrays."""
        region = Region()
        region.spo.nchan = np.array([1, 2, 3])
        region.res.nchan = np.array([1, 2])
        assert region.check() == -1

    def test_increase_region_numbers(self):
        """Tests that the region numbers can be increased by an integer amount."""
        region = Region()
        region.res.nregion = 1
        region.res.region = np.array([1, 2, 3])
        region.increase_region(2)
        assert np.array_equal(region.res.region, np.array([3, 4, 5]))

    def test_check_single_region(self):
        """Tests that the check method correctly identifies when the arrays consist of more than one region."""
        region = Region()
        region.spo.nchan = np.array([1, 2, 3])
        region.spo.nregion = 2
        assert region.check(nregion=True) == -1
