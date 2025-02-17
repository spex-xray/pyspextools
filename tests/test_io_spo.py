import pytest
import numpy as np
from pyspextools.io.spo import Spo


class TestSpo:
    """
    Code Analysis

    Main functionalities:
    The Spo class is designed to handle and manipulate spectral data from X-ray observations. It provides methods for
    reading and writing FITS files, adding and deleting spectral regions, checking the consistency of the data, and
    swapping the order of the data. The class also includes fields to store various properties of the spectral data,
    such as energy ranges, exposure times, source rates, and errors.

    Methods:
    - __init__: Initializes the Spo object and sets its initial fields to empty or default values.
    - zero_spo: Sets all the fields related to spectral data to zero or ones, depending on the type of data.
    - add_spo_region: Adds a spectral region from another Spo object to the current object.
    - del_spo_region: Deletes a spectral region from the current object.
    - read_file: Reads spectral data from a FITS file and populates the fields of the Spo object.
    - return_region: Returns a new Spo object containing the spectral data for a specific region.
    - write_file: Writes the spectral data to a FITS file.
    - swap_order: Swaps the order of the spectral data.
    - check: Checks the consistency of the spectral data and raises exceptions if any inconsistencies are found.
    - check_filename: Checks if the output filename has the correct extension and renames it if necessary.
    - get_mask: Sets the mask fields to select a specific spectral region.
    - show: Prints information about the spectral data for a specific region.

    Fields:
    - sponame: The name of the FITS file containing the spectral data.
    - empty: A boolean flag indicating if the Spo object is empty or not.
    - nregion: The number of spectral regions in the data.
    - nchan: An array storing the number of data channels for each spectral region.
    - echan1, echan2: Arrays storing the lower and upper energy limits for each data channel.
    - tints: An array storing the exposure times for each data channel.
    - ochan, dochan: Arrays storing the source rates and their errors for each data channel.
    - mbchan, dbchan: Arrays storing the background rates and their errors for each data channel.
    - brat: An array storing the exposure rates for each data channel.
    - ssys, bsys: Arrays storing the systematic errors for the source and background rates.
    - used, first, last: Arrays storing flags indicating if a data channel is used, the first channel of a region, and the last channel of a region, respectively.
    - brat_exist: A boolean flag indicating if the exposure rates exist in the data.
    - swap: A boolean flag indicating if the order of the data has been swapped.
    - anames: A dictionary mapping the field names to their corresponding descriptions.
    - mask_region, mask_spectrum: Arrays used as masks to select specific spectral regions and data channels.
    """

    def test_initialize_spo(self):
        """Tests that a new instance of Spo class is properly initialized."""
        spo = Spo()
        assert spo.sponame == ''
        assert spo.empty == True
        assert spo.nregion == 0
        assert np.array_equal(spo.nchan, np.array([], dtype=int))
        assert np.array_equal(spo.echan1, np.array([], dtype=float))
        assert np.array_equal(spo.echan2, np.array([], dtype=float))
        assert np.array_equal(spo.tints, np.array([], dtype=float))
        assert np.array_equal(spo.ochan, np.array([], dtype=float))
        assert np.array_equal(spo.dochan, np.array([], dtype=float))
        assert np.array_equal(spo.mbchan, np.array([], dtype=float))
        assert np.array_equal(spo.dbchan, np.array([], dtype=float))
        assert np.array_equal(spo.brat, np.array([], dtype=float))
        assert np.array_equal(spo.ssys, np.array([], dtype=float))
        assert np.array_equal(spo.bsys, np.array([], dtype=float))
        assert np.array_equal(spo.used, np.array([], dtype=bool))
        assert np.array_equal(spo.first, np.array([], dtype=bool))
        assert np.array_equal(spo.last, np.array([], dtype=bool))
        assert spo.brat_exist == True
        assert spo.swap == False
        assert spo.anames == {'echan1': 'Lower_Energy', 'echan2': 'Upper_Energy', 'tints': 'Exposure_Time',
                              'ochan': 'Source_Rate', 'dochan': 'Err_Source_Rate', 'mbchan': 'Back_Rate',
                              'dbchan': 'Err_Back_Rate', 'brat': 'Exp_Rate', 'ssys': 'Sys_Source', 'bsys': 'Sys_Back',
                              'used': 'Used', 'first': 'First', 'last': 'Last'}
        assert np.array_equal(spo.mask_region, np.array([], dtype=bool))
        assert np.array_equal(spo.mask_spectrum, np.array([], dtype=bool))

    def test_add_region(self):
        """Tests that a region can be added to a Spo object."""
        spo = Spo()
        spo.zero_spo(3)
        origspo = Spo()
        origspo.zero_spo(3)
        origspo.echan1 = np.array([1.0, 2.0, 3.0])
        origspo.echan2 = np.array([2.0, 3.0, 4.0])
        origspo.tints = np.array([10.0, 20.0, 30.0])
        origspo.ochan = np.array([100.0, 200.0, 300.0])
        origspo.dochan = np.array([1.0, 2.0, 3.0])
        origspo.mbchan = np.array([50.0, 100.0, 150.0])
        origspo.dbchan = np.array([5.0, 10.0, 15.0])
        origspo.brat = np.array([1.0, 2.0, 3.0])
        origspo.ssys = np.array([0.1, 0.2, 0.3])
        origspo.bsys = np.array([0.01, 0.02, 0.03])
        origspo.used = np.array([True, True, True])
        origspo.first = np.array([True, True, True])
        origspo.last = np.array([True, True, True])
        spo.add_spo_region(origspo)
        assert np.array_equal(spo.nchan, np.array([3, 3]))
        assert np.array_equal(spo.echan1, np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0]))
        assert np.array_equal(spo.echan2, np.array([0.0, 0.0, 0.0, 2.0, 3.0, 4.0]))
        assert np.array_equal(spo.tints, np.array([0.0, 0.0, 0.0, 10.0, 20.0, 30.0]))
        assert np.array_equal(spo.ochan, np.array([0.0, 0.0, 0.0, 100.0, 200.0, 300.0]))
        assert np.array_equal(spo.dochan, np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0]))
        assert np.array_equal(spo.mbchan, np.array([0.0, 0.0, 0.0, 50.0, 100.0, 150.0]))
        assert np.array_equal(spo.dbchan, np.array([0.0, 0.0, 0.0, 5.0, 10.0, 15.0]))
        assert np.array_equal(spo.brat, np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0]))
        assert np.array_equal(spo.ssys, np.array([0.0, 0.0, 0.0, 0.1, 0.2, 0.3]))
        assert np.array_equal(spo.bsys, np.array([0.0, 0.0, 0.0, 0.01, 0.02, 0.03]))
        assert np.array_equal(spo.used, np.array([True, True, True, True, True, True]))
        assert np.array_equal(spo.first, np.array([True, True, True, True, True, True]))
        assert np.array_equal(spo.last, np.array([True, True, True, True, True, True]))
        assert spo.empty == False

    def test_delete_region(self):
        """Tests that a region can be deleted from a Spo object."""
        spo = Spo()
        spo.zero_spo(3)
        origspo = Spo()
        origspo.zero_spo(3)
        origspo.echan1 = np.array([1.0, 2.0, 3.0])
        origspo.echan2 = np.array([2.0, 3.0, 4.0])
        origspo.tints = np.array([10.0, 20.0, 30.0])
        origspo.ochan = np.array([100.0, 200.0, 300.0])
        origspo.dochan = np.array([1.0, 2.0, 3.0])
        origspo.mbchan = np.array([50.0, 100.0, 150.0])
        origspo.dbchan = np.array([5.0, 10.0, 15.0])
        origspo.brat = np.array([1.0, 2.0, 3.0])
        origspo.ssys = np.array([0.1, 0.2, 0.3])
        origspo.bsys = np.array([0.01, 0.02, 0.03])
        origspo.used = np.array([True, True, True])
        origspo.first = np.array([True, True, True])
        origspo.last = np.array([True, True, True])
        spo.add_spo_region(origspo)
        spo.del_spo_region(1)
        assert np.array_equal(spo.nchan, np.array([3], dtype=int))
        assert np.array_equal(spo.echan1, np.array([1.0, 2.0, 3.0], dtype=float))
        assert np.array_equal(spo.echan2, np.array([2.0, 3.0, 4.0], dtype=float))
        assert np.array_equal(spo.tints, np.array([10.0, 20.0, 30.0], dtype=float))
        assert np.array_equal(spo.ochan, np.array([100.0, 200.0, 300.0], dtype=float))
        assert np.array_equal(spo.dochan, np.array([1.0, 2.0, 3.0], dtype=float))
        assert np.array_equal(spo.mbchan, np.array([50.0, 100.0, 150.0], dtype=float))
        assert np.array_equal(spo.dbchan, np.array([5.0, 10.0, 15.0], dtype=float))
        assert np.array_equal(spo.brat, np.array([1.0, 2.0, 3.0], dtype=float))
        assert np.array_equal(spo.ssys, np.array([0.1, 0.2, 0.3], dtype=float))
        assert np.array_equal(spo.bsys, np.array([0.01, 0.02, 0.03], dtype=float))
        assert np.array_equal(spo.used, np.array([True, True, True], dtype=bool))
        assert np.array_equal(spo.first, np.array([True, True, True], dtype=bool))
        assert np.array_equal(spo.last, np.array([True, True, True], dtype=bool))
        assert spo.empty == False

    def test_read_file(self):
        """Tests that data can be read from a FITS file into a Spo object."""
        spo = Spo()
        spo.read_file('data/test_write.spo')
        assert spo.nregion == 1
        assert np.array_equal(spo.nchan, np.array([3]))
        assert np.array_equal(spo.echan1, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.echan2, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.tints, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.ochan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.dochan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.mbchan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.dbchan, np.array([.0, 0.0, 0.0]))
        assert np.array_equal(spo.brat, np.array([1.0, 1.0, 1.0]))
        assert np.array_equal(spo.ssys, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.bsys, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo.used, np.array([True, True, True]))
        assert np.array_equal(spo.first, np.array([True, True, True]))
        assert np.array_equal(spo.last, np.array([True, True, True]))
        assert spo.empty == False

    def test_write_file(self):
        """Tests that data from a Spo object can be written to a FITS file."""
        spo = Spo()
        spo.zero_spo(3)
        spo.write_file('data/test_write.spo', overwrite=True)
        spo2 = Spo()
        spo2.read_file('data/test_write.spo')
        assert spo2.nregion == 1
        assert np.array_equal(spo2.nchan, np.array([3]))
        assert np.array_equal(spo2.echan1, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.echan2, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.tints, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.ochan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.dochan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.mbchan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.dbchan, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.brat, np.array([1.0, 1.0, 1.0]))
        assert np.array_equal(spo2.ssys, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.bsys, np.array([0.0, 0.0, 0.0]))
        assert np.array_equal(spo2.used, np.array([True, True, True]))
        assert np.array_equal(spo2.first, np.array([True, True, True]))
        assert np.array_equal(spo2.last, np.array([True, True, True]))
        assert spo2.empty == False

    def test_check_consistency(self):
        """Tests that the consistency of a Spo object can be checked."""
        spo = Spo()
        spo.zero_spo(3)
        spo.echan1 = np.array([1.0, 2.0, 3.0])
        spo.echan2 = np.array([2.0, 3.0, 4.0])
        spo.tints = np.array([10.0, 20.0, 30.0])
        spo.ochan = np.array([100.0, 200.0, 300.0])
        spo.dochan = np.array([1.0, 2.0, 3.0])
        spo.mbchan = np.array([50.0, 100.0, 150.0])
        spo.dbchan = np.array([5.0, 10.0, 15.0])
        spo.brat = np.array([1.0, 2.0, 3.0])
        spo.ssys = np.array([0.1, 0.2, 0.3])
        spo.bsys = np.array([0.01, 0.02, 0.03])
        spo.used = np.array([True, True, True])
        spo.first = np.array([True, True, True])
        spo.last = np.array([True, True, True])
        assert spo.check() == 0

    def test_initialize_empty_spo(self):
        """Tests that a Spo object can be initialized with empty arrays."""
        spo = Spo()
        assert spo.sponame == ''
        assert spo.empty == True
        assert spo.nregion == 0
        assert np.array_equal(spo.nchan, np.array([], dtype=int))
        assert np.array_equal(spo.echan1, np.array([], dtype=float))
        assert np.array_equal(spo.echan2, np.array([], dtype=float))
        assert np.array_equal(spo.tints, np.array([], dtype=float))
        assert np.array_equal(spo.ochan, np.array([], dtype=float))
        assert np.array_equal(spo.dochan, np.array([], dtype=float))
        assert np.array_equal(spo.mbchan, np.array([], dtype=float))
        assert np.array_equal(spo.dbchan, np.array([], dtype=float))
        assert np.array_equal(spo.brat, np.array([], dtype=float))
        assert np.array_equal(spo.ssys, np.array([], dtype=float))
        assert np.array_equal(spo.bsys, np.array([], dtype=float))
        assert np.array_equal(spo.used, np.array([], dtype=bool))
        assert np.array_equal(spo.first, np.array([], dtype=bool))
        assert np.array_equal(spo.last, np.array([], dtype=bool))
        assert spo.brat_exist == True
        assert spo.swap == False
        assert spo.anames == {'echan1': 'Lower_Energy', 'echan2': 'Upper_Energy', 'tints': 'Exposure_Time', 'ochan': 'Source_Rate', 'dochan': 'Err_Source_Rate', 'mbchan': 'Back_Rate', 'dbchan': 'Err_Back_Rate', 'brat': 'Exp_Rate', 'ssys': 'Sys_Source', 'bsys': 'Sys_Back', 'used': 'Used', 'first': 'First', 'last': 'Last'}
        assert np.array_equal(spo.mask_region, np.array([], dtype=bool))
        assert np.array_equal(spo.mask_spectrum, np.array([], dtype=bool))

    def test_add_region_invalid_index(self):
        """Tests that an error is raised when trying to add a region with an invalid index."""
        spo = Spo()
        origspo = Spo()
        with pytest.raises(Exception):
            spo.add_spo_region(origspo, 0)
        with pytest.raises(Exception):
            spo.add_spo_region(origspo, -1)
        with pytest.raises(Exception):
            spo.add_spo_region(origspo, 2)

    def test_delete_region_invalid_index(self):
        """Tests that an error is raised when trying to delete a region with an invalid index."""
        spo = Spo()
        with pytest.raises(Exception):
            spo.del_spo_region(0)
        with pytest.raises(Exception):
            spo.del_spo_region(-1)
