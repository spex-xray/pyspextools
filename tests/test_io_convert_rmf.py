import pytest
from pyspextools.io.convert import rmf_to_res
from pyspextools.io.rmf import Rmf
from pyspextools.io.arf import Arf
from pyspextools.io.res import Res


class TestRmfToRes:
    """
    Code Analysis

    Objective:
    - The objective of the 'rmf_to_res' function is to convert an OGIP response matrix object to a SPEX format response matrix object. The function translates the response matrix one-to-one without optimizations and provides an optional ARF effective area object.

    Inputs:
    - rmf: an OGIP response matrix object
    - matext: an integer representing the RMF matrix number to convert (start counting at 0)
    - arf: an optional ARF effective area object

    Flow:
    - Check if the supplied matrix extension number is valid
    - Check if an ARF object is provided
    - Read the number of energy bins and groups
    - Read the total number of groups (which is neg in SPEX format)
    - Read the total number of matrix elements
    - Set the number of components to 1 (no optimization or re-ordering)
    - Read the energy bin boundaries and group information
    - Convert matrix to m^2 units for SPEX
    - Check if channel order needs to be swapped
    - Return a pyspextools Res object containing the response matrix

    Outputs:
    - A pyspextools Res object containing the response matrix

    Additional aspects:
    - The function raises a ValueError if the supplied matrix extension number is not valid or if there is a mismatch between the number of groups or matrix elements.
    - The function also displays warning and error messages if there are issues with the input data.
    """

    def test_valid_input_rmf_no_arf(self):
        """Tests that the function works with a valid input RMF and no ARF."""
        rmf = Rmf()
        rmf.read("data/rmf_valid.rmf")
        res = rmf_to_res(rmf)
        assert isinstance(res, Res)
        assert res.nchan[0] == 100
        assert res.neg[0] == 100
        assert res.ncomp == 1

    def test_valid_input_rmf_with_arf_cm2(self):
        """Tests that the function works with a valid input RMF and ARF with ARFUnits as 'cm2'."""
        rmf = Rmf()
        rmf.read("data/rmf_valid.rmf")
        arf = Arf()
        arf.read("data/arf.arf")
        res = rmf_to_res(rmf, arf=arf)
        assert isinstance(res, Res)
        assert res.nchan[0] == 100
        assert res.neg[0] == 100
        assert res.ncomp == 1

    def test_invalid_matrix_extension_number(self):
        """Tests that the function raises a ValueError with an invalid matrix extension number."""
        rmf = Rmf()
        rmf.read("data/rmf_valid.rmf")
        with pytest.raises(ValueError):
            rmf_to_res(rmf, matext=10)

    def test_uninitialized_ogip_response_matrix(self):
        """Tests that the function raises a NameError with an uninitialized OGIP response matrix."""
        rmf = Rmf()
        with pytest.raises(ValueError):
            rmf_to_res(rmf)

    def test_discontinuous_bins_in_energy_array(self):
        """Tests that the function raises a ValueError with discontinuous bins in energy array."""
        rmf = Rmf()
        rmf.read("data/rmf_discontinuous.rmf")
        with pytest.raises(ValueError):
            rmf_to_res(rmf)
