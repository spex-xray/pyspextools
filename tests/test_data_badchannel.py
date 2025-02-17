import pytest
from pyspextools.data.badchannels import clean_region
from pyspextools.io.region import Region
from pyspextools.io.spo import Spo
from pyspextools.io.res import Res
import numpy as np


class TestCleanRegion:
    """
    Objective:
    - The objective of the function is to remove bad channels and channels with zero response from the input Region object.

    Inputs:
    - The function takes in an input Region object (reg) of type pyspextools.io.Region.

    Flow:
    - The function first checks if the input object is of type Region and if the spo and res objects are not empty.
    - It then calls the __get_bad_channel_masks function to identify bad channels and create masks for channels, groups,
      and response elements.
    - The function then removes the bad channels from the spectral region and updates the spo object accordingly.
    - It also removes the bad channels from the response matrix and updates the res object accordingly.
    - Finally, the function returns the updated Region object.

    Outputs:
    - The main output of the function is the updated Region object with bad channels and response elements removed.

    Additional aspects:
    - The function checks the consistency of the updated spo and res objects using their respective check functions.
    - It also prints the number of good and bad channels, groups, and response elements before and after the cleaning
      process.
    - The function raises ValueErrors if the input object is not of type Region or if the spo or res objects are empty.
    """

    def test_behaviour_input_object_not_of_type_Region(self):
        """Tests that the function raises a ValueError when the input object is not of type Region."""
        with pytest.raises(ValueError):
            clean_region(1)

    def test_behaviour_input_spo_object_empty(self):
        """Tests that the function raises a ValueError when the input region object is empty."""
        with pytest.raises(ValueError):
            clean_region(Region())

    def test_behaviour_mismatch_in_number_of_channels_in_spo_object(self):
        """Tests that the function raises a ValueError when there is a mismatch in the number of channels in the
        spo object."""
        reg = Region()
        reg.spo.nchan = 10
        reg.spo.used = np.zeros(10)
        reg.res.nc = np.array([1, 2, 3])
        with pytest.raises(ValueError):
            clean_region(reg)

    def test_behaviour_mismatch_in_icomp_group_numbers(self):
        """Tests that the function raises a ValueError when there is a mismatch between the number of groups in the
        ICOMP and GROUP extensions."""
        reg = Region()
        reg.spo.nchan = 10
        reg.spo.use = np.zeros(10)
        reg.res.nc = np.array([1, 2, 3])
        reg.res.neg = np.array([1, 2])
        with pytest.raises(ValueError):
            clean_region(reg)

    def test_behaviour_all_channels_are_good(self):
        """Tests that the function does not remove bad channels from the spectral region when all channels are good."""
        reg = Region()
        reg.spo = Spo()
        reg.res = Res()
        reg.spo.nchan = np.array([3])
        reg.spo.echan1 = np.array([1., 2., 3.])
        reg.spo.echan2 = np.array([2., 3., 4.])
        reg.spo.tints = np.array([10., 10., 10.])
        reg.spo.ochan = np.array([9., 9., 9.])
        reg.spo.dochan = np.array([3., 3., 3.])
        reg.spo.mbchan = np.zeros(3)
        reg.spo.dbchan = np.zeros(3)
        reg.spo.brat = np.ones(3)
        reg.spo.ssys = np.zeros(3)
        reg.spo.bsys = np.zeros(3)
        reg.spo.first = np.ones(3, dtype=bool)
        reg.spo.last = np.ones(3, dtype=bool)
        reg.spo.used = np.ones(3, dtype=bool)
        reg.spo.empty = False
        reg.res.neg = np.array([3])
        reg.res.nc = np.array([3, 3, 3])
        reg.res.eg1 = np.array([1., 2., 3.])
        reg.res.eg2 = np.array([2., 3., 4.])
        reg.res.ic1 = np.array([1, 1, 1])
        reg.res.ic2 = np.array([3, 3, 3])
        reg.res.resp = np.ones(9)
        reg.res.nchan = np.array([3])
        reg.res.empty = False
        cleaned_reg = clean_region(reg)
        assert np.array_equal(cleaned_reg.spo.used, np.ones(3, dtype=bool))
        assert np.array_equal(cleaned_reg.res.resp, np.ones(9))

    def test_behaviour_all_channels_are_bad(self):
        """Tests that the function correctly handles the case when all channels are bad."""
        reg = Region()
        reg.spo = Spo()
        reg.res = Res()
        reg.spo.used = np.zeros(10, dtype=bool)
        reg.res.resp = np.zeros(10)
        with pytest.raises(ValueError):
            clean_region(reg)

    def test_behaviour_function_correctly_reindexes_matrix(self):
        """Tests that the function correctly re-indexes the matrix."""
        reg = Region()
        reg.spo = Spo()
        reg.res = Res()
        reg.spo.nregion = 1
        reg.spo.nchan = np.array([3])
        reg.spo.echan1 = np.array([1., 2., 3.])
        reg.spo.echan2 = np.array([2., 3., 4.])
        reg.spo.tints = np.array([10., 10., 10.])
        reg.spo.ochan = np.array([9., 9., 9.])
        reg.spo.dochan = np.array([3., 3., 3.])
        reg.spo.mbchan = np.zeros(3)
        reg.spo.dbchan = np.zeros(3)
        reg.spo.brat = np.ones(3)
        reg.spo.ssys = np.zeros(3)
        reg.spo.bsys = np.zeros(3)
        reg.spo.first = np.ones(3, dtype=bool)
        reg.spo.last = np.ones(3, dtype=bool)
        reg.spo.used = np.array([True, False, True])
        reg.spo.empty = False
        reg.res.neg = np.array([3])
        reg.res.nc = np.array([3, 3, 3])
        reg.res.eg1 = np.array([1., 2., 3.])
        reg.res.eg2 = np.array([2., 3., 4.])
        reg.res.ic1 = np.array([1, 1, 1])
        reg.res.ic2 = np.array([3, 3, 3])
        reg.res.resp = np.ones(9)
        reg.res.nchan = np.array([3])
        reg.res.empty = False
        cleaned_reg = clean_region(reg)
        assert np.array_equal(cleaned_reg.spo.used, np.array([True, True]))
        assert np.array_equal(cleaned_reg.res.resp, np.ones(6))
