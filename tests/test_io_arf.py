
import pytest
from pyspextools.io.arf import Arf
from astropy.io import fits
import numpy as np

"""
Code Analysis

Main functionalities:
The Arf class is designed to read and write OGIP ARF files, which contain information about the effective area of a 
telescope or instrument as a function of energy. The class provides methods to read in the ARF data from a FITS file, 
write the ARF data to a new FITS file, and check if the basic information has been read in correctly. The class also 
includes fields to store the ARF data and associated metadata, such as the energy units and grating information.

Methods:
- __init__(self): Initializes an Arf object with empty arrays for the LowEnergy, HighEnergy, and EffArea fields, 
  and default values for the EnergyUnits, ARFUnits, Order, and Grating fields.
- read(self, arffile): Reads in the ARF data from a FITS file specified by the arffile parameter. The LowEnergy, 
  HighEnergy, and EffArea fields are populated with the data from the file, and the EnergyUnits, ARFUnits, Order, 
  and Grating fields are updated with the corresponding metadata from the file header.
- write(self, arffile, telescop=None, instrume=None, filter=None, overwrite=False): Writes the ARF data to a new 
  FITS file specified by the arffile parameter. The optional telescop, instrume, and filter parameters can be used 
  to set the TELESCOP, INSTRUME, and FILTER keywords in the file header. The overwrite parameter can be used to 
  specify whether an existing file should be overwritten.
- check(self): Checks if the LowEnergy and EffArea fields have been populated with data. Returns 0 if the fields 
  are non-empty, and 1 otherwise.
- disp(self): Displays a summary of the ARF object, including the size of the LowEnergy, HighEnergy, and EffArea 
  arrays, and the values of the EnergyUnits and ARFUnits fields.

Fields:
- LowEnergy: A numpy array containing the low energy boundaries of each energy bin in the ARF data.
- HighEnergy: A numpy array containing the high energy boundaries of each energy bin in the ARF data.
- EffArea: A numpy array containing the effective area of each energy bin in the ARF data.
- EnergyUnits: A string specifying the units of energy used in the ARF data.
- ARFUnits: A string specifying the units of effective area used in the ARF data.
- Order: An integer specifying the grating order (if applicable) used in the ARF data.
- Grating: An integer specifying the grating instrument (if applicable) used in the ARF data.
"""


class TestArf:

    def test_read_success(self):
        """Tests that an OGIP ARF file can be read successfully."""
        arf = Arf()
        arf.read('data/arf.arf')
        assert len(arf.LowEnergy) == 100
        assert len(arf.HighEnergy) == 100
        assert len(arf.EffArea) == 100
        assert arf.EnergyUnits == 'keV'
        assert arf.ARFUnits == 'cm2'
        assert arf.Order == 0
        assert arf.Grating == 0

    def test_write_success(self, tmp_path):
        """Tests that an OGIP ARF file can be written successfully."""
        arf = Arf()
        arf.LowEnergy = np.array([1, 2, 3])
        arf.HighEnergy = np.array([2, 3, 4])
        arf.EffArea = np.array([3, 4, 5])
        arf.EnergyUnits = 'keV'
        arf.ARFUnits = 'cm2'
        arf.Order = 0
        arf.Grating = 0
        arffile = 'tmp/test_arf.fits'
        arf.write(arffile, overwrite=True)
        with fits.open(arffile) as hdul:
            data = hdul['SPECRESP'].data
            header = hdul['SPECRESP'].header
        assert np.allclose(data['ENERG_LO'], [1, 2, 3])
        assert np.allclose(data['ENERG_HI'], [2, 3, 4])
        assert np.allclose(data['SPECRESP'], [3, 4, 5])
        assert header['TUNIT1'] == 'keV'
        assert header['TUNIT3'] == 'cm2'

    def test_check_success(self):
        """Tests that basic information can be read in successfully."""
        arf = Arf()
        arf.LowEnergy = np.array([1, 2, 3])
        arf.HighEnergy = np.array([2, 3, 4])
        arf.EffArea = np.array([3, 4, 5])
        assert arf.check() == 0

    def test_read_empty_file(self):
        """Tests that an empty OGIP ARF file can be read."""
        arf = Arf()
        with pytest.raises(IndexError):
            arf.read('data/arf_empty.arf')
        assert len(arf.LowEnergy) == 0
        assert len(arf.HighEnergy) == 0
        assert len(arf.EffArea) == 0
        assert arf.EnergyUnits == 'keV'
        assert arf.ARFUnits == 'cm2'
        assert arf.Order == 0
        assert arf.Grating == 0

    def test_read_missing_keywords(self):
        """Tests that an OGIP ARF file with missing header keywords can be read."""
        arf = Arf()
        arf.read('data/arf_missing_keywords.arf')
        assert len(arf.LowEnergy) == 100
        assert len(arf.HighEnergy) == 100
        assert len(arf.EffArea) == 100
        assert arf.EnergyUnits == 'keV'
        assert arf.ARFUnits == 'cm2'
        assert arf.Order == 0
        assert arf.Grating == 0

    def test_write_missing_keywords(self):
        """Tests that an OGIP ARF file with missing header keywords can be written."""
        arf = Arf()
        arf.LowEnergy = np.array([1, 2, 3])
        arf.HighEnergy = np.array([4, 5, 6])
        arf.EffArea = np.array([7, 8, 9])
        arf.EnergyUnits = 'keV'
        arf.ARFUnits = 'cm2'
        arf.Order = 0
        arf.Grating = 0
        arf.write('tmp/test_arf.arf', overwrite=True)
        with fits.open('tmp/test_arf.arf') as hdul:
            header = hdul['SPECRESP'].header
        assert header['TELESCOP'] == 'None'
        assert header['INSTRUME'] == 'None'
        assert header['FILTER'] == 'None'

    def test_read_nan_values(self):
        """Tests that an OGIP ARF file with NaN values can be read."""
        arf = Arf()
        arf.read('data/arf_nan.arf')
        assert np.isnan(arf.EffArea).any() == False
