import pytest
from pyspextools.io.res import Res
import numpy as np
import os


class TestRes:
    """
    Code Analysis

    Main functionalities:
    - The class represents a response matrix for spectroscopic analysis.
    - It allows adding and removing regions from the response matrix.
    - It can read and write response matrices from/to FITS files.
    - It can return a subset of the response matrix for a specific sector and region.
    - It can swap the order of the response matrix.
    - It can append another response matrix to the existing one.
    - It can perform channel shifting on the response matrix.
    - It can perform various checks on the response matrix.

    Methods:
    - `__init__(self)`: Initializes the class and sets the initial values for all fields.
    - `add_res_region(self, origres, isector=1, iregion=1)`: Adds a region from another response matrix to the current one.
    - `del_res_region(self, isector, iregion)`: Removes a region from the response matrix.
    - `read_file(self, resfile)`: Reads a response matrix from a FITS file.
    - `return_region(self, isector, iregion)`: Returns a subset of the response matrix for a specific sector and region.
    - `write_file(self, resfile, overwrite=False, history=None)`: Writes the response matrix to a FITS file.
    - `swap_order(self)`: Swaps the order of the response matrix.
    - `append_component(self, addres, iregion=1, isector=1)`: Appends another response matrix to the current one.
    - `get_mask(self, isector, iregion)`: Generates masks for selecting a specific sector and region in the response matrix.
    - `channel_shift(self, shift)`: Performs channel shifting on the response matrix.
    - `check(self)`: Performs various checks on the response matrix.
    - `check_filename(self, filename)`: Checks if the output filename has the correct extension and renames it if necessary.
    - `show(self, iregion=1, isector=1)`: Prints information about the response matrix.

    Fields:
    - `resname`: Name of the response file.
    - `empty`: Flag indicating if the response matrix is empty.
    - `nchan`: Array of data channel numbers.
    - `neg`: Array of number of energy bins per component.
    - `sector`: Array of sector numbers.
    - `region`: Array of region numbers.
    - `shcomp`: Array of component numbers.
    - `nsector`: Number of sectors.
    - `nregion`: Number of regions.
    - `ncomp`: Number of components.
    - `share_comp`: Flag indicating if components are shared between regions.
    - `area_scal`: Flag indicating if area scaling is applied.
    - `resp_der`: Flag indicating if response derivatives are included.
    - `eg1`: Array of lower energy bin edges.
    - `eg2`: Array of upper energy bin edges.
    - `ic1`: Array of lower channel indices.
    - `ic2`: Array of upper channel indices.
    - `nc`: Array of number of channels per group.
    - `relarea`: Array of relative areas.
    - `resp`: Array of response values.
    - `dresp`: Array of response derivative values.
    - `mask_resp`: Mask for selecting response values.
    - `mask_group`: Mask for selecting group values.
    - `mask_icomp`: Mask for selecting component values.
    - `swap`: Flag indicating if the response matrix has been swapped.
    """

    def test_create_instance(self):
        """Tests that an instance of the 'Res' class can be created."""
        res = Res()
        assert isinstance(res, Res)

    def test_add_region(self):
        """Tests that a region can be added to the response."""
        res = Res()
        origres = Res()
        origres.nchan = np.array([3])
        origres.neg = np.array([3])
        origres.sector = np.array([1])
        origres.region = np.array([1])
        res.add_res_region(origres)
        assert np.array_equal(res.nchan, np.array([3]))
        assert np.array_equal(res.neg, np.array([3]))
        assert np.array_equal(res.sector, np.array([1]))
        assert np.array_equal(res.region, np.array([1]))

    def test_delete_region(self):
        """Tests that a region can be deleted from the response."""
        res = Res()
        res.nchan = np.array([3])
        res.neg = np.array([3])
        res.sector = np.array([1])
        res.region = np.array([1])
        res.del_res_region(1, 1)
        assert np.array_equal(res.nchan, np.array([]))
        assert np.array_equal(res.neg, np.array([]))
        assert np.array_equal(res.sector, np.array([]))
        assert np.array_equal(res.region, np.array([]))

    def test_read_response_file(self):
        """Tests that a response file can be read"""
        res = Res()
        res.read_file('data/test.res')
        assert res.nsector == 1
        assert res.nregion == 1
        assert res.ncomp == 1
        assert res.share_comp == False
        assert res.area_scal == False
        assert res.resp_der == False

    def test_write_response_file(self):
        """Tests that a response file can be written."""
        res = Res()
        res.nsector = 1
        res.nregion = 1
        res.ncomp = 1
        res.share_comp = False
        res.area_scal = False
        res.resp_der = False
        res.nchan = np.array([3])
        res.neg = np.array([3])
        res.sector = np.array([1])
        res.region = np.array([1])
        res.eg1 = np.array([1., 2., 3.])
        res.eg2 = np.array([2., 3., 4.])
        res.ic1 = np.array([1, 1, 1])
        res.ic2 = np.array([3, 3, 3])
        res.nc = np.array([3, 3, 3])
        res.resp = np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1])
        res.write_file('tmp/test_w.res')
        assert os.path.exists('tmp/test_w.res')
        os.remove('tmp/test_w.res')

    def test_swap_order(self):
        """Tests that the order of the response can be swapped."""
        res = Res()
        res.read_file('data/test.res')
        res.swap_order()
        assert np.array_equal(res.ic1, np.array([1, 1, 1]))
        assert np.array_equal(res.ic2, np.array([3, 3, 3]))
        assert np.array_equal(res.resp, np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]))

    def test_append_component(self):
        """Tests that a component can be appended to the response."""
        res = Res()
        addres = Res()
        addres.nchan = np.array([3])
        addres.neg = np.array([3])
        addres.eg1 = np.array([1.0, 2.0, 3.0])
        addres.eg2 = np.array([2.0, 3.0, 4.0])
        addres.sector = np.array([1])
        addres.region = np.array([1])
        addres.ic1 = np.array([0, 0, 0])
        addres.ic2 = np.array([2, 2, 2])
        addres.resp = np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1])
        addres.dresp = np.array([0., 0., 0., 0., 0.1, 0., 0., 0., 0.])
        res.resp_der = True
        res.append_component(addres)
        assert np.array_equal(res.nchan, np.array([3]))
        assert np.array_equal(res.neg, np.array([3]))
        assert np.array_equal(res.sector, np.array([1]))
        assert np.array_equal(res.region, np.array([1]))
        assert np.array_equal(res.ic1, np.array([0, 0, 0]))
        assert np.array_equal(res.ic2, np.array([2, 2, 2]))
        assert np.array_equal(res.resp, np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]))
        assert np.array_equal(res.dresp, np.array([0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0]))

    def test_get_mask(self):
        """Tests that the mask for a specific sector and region can be obtained."""
        res = Res()
        res.nsector = 1
        res.nregion = 1
        res.ncomp = 1
        res.share_comp = False
        res.area_scal = False
        res.resp_der = False
        res.nchan = np.array([3])
        res.neg = np.array([3])
        res.eg1 = np.array([1.0, 2.0, 3.0])
        res.eg2 = np.array([2.0, 3.0, 4.0])
        res.sector = np.array([1])
        res.region = np.array([1])
        res.ic1 = np.array([0, 0, 0])
        res.ic2 = np.array([2, 2, 2])
        res.resp = np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1])
        res.get_mask(1, 1)
        assert np.array_equal(res.mask_resp, np.array([False, False, False, False, False, False, False, False, False]))
        assert np.array_equal(res.mask_group, np.array([True, True, True]))
        assert np.array_equal(res.mask_icomp, np.array([True]))

    def test_shift_channels(self):
        """Tests that the channels in the response can be shifted."""
        res = Res()
        res.nchan = np.array([3])
        res.neg = np.array([3])
        res.eg1 = np.array([1.0, 2.0, 3.0])
        res.eg2 = np.array([2.0, 3.0, 4.0])
        res.sector = np.array([1])
        res.region = np.array([1])
        res.ic1 = np.array([0, 0, 0])
        res.ic2 = np.array([2, 2, 2])
        res.resp = np.array([0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1])
        res.dresp = np.array([0., 0., 0., 0., 0.1, 0., 0., 0., 0.])
        res.channel_shift(1)
        assert np.array_equal(res.ic1, np.array([1, 1, 1]))
        assert np.array_equal(res.ic2, np.array([3, 3, 3]))
