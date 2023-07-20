import pytest
from pyspextools.io.rmf import RmfEbounds

"""
Code Analysis

Main functionalities:
The RmfEbounds class is designed to read the EBOUNDS extension from an RMF or RSP file. It contains fields to store 
the channel numbers, start and end energy of each channel, the number of data channels, and the unit of the energy 
scale. The read method reads the EBOUNDS table from the input file and populates the fields accordingly.

Methods:
- read(rmffile): reads the EBOUNDS table from the input RMF or RSP file and populates the fields of the class 
  accordingly.

Fields:
- FirstChannel: the first channel number
- Channel: an array of channel numbers
- ChannelLowEnergy: an array of start energy of each channel
- ChannelHighEnergy: an array of end energy of each channel
- NumberChannels: the number of data channels
- EnergyUnits: the unit of the energy scale.
"""


class TestRmfEbounds:

    def test_read_valid_rmf_file(self):
        """Tests reading a valid RMF file with EBOUNDS extension."""
        ebounds = RmfEbounds()
        ebounds.read('data/rmf_valid.rmf')
        assert ebounds.NumberChannels == 100
        assert ebounds.FirstChannel == 1
        assert ebounds.ChannelLowEnergy[0] == 1.000000000
        assert ebounds.ChannelHighEnergy[-1] == 11.00000000
        assert ebounds.EnergyUnits == 'keV'

    def test_attributes_initialized(self):
        """Tests that all attributes are correctly initialized."""
        ebounds = RmfEbounds()
        assert ebounds.FirstChannel == 0
        assert len(ebounds.Channel) == 0
        assert len(ebounds.ChannelLowEnergy) == 0
        assert len(ebounds.ChannelHighEnergy) == 0
        assert ebounds.NumberChannels == 0
        assert ebounds.EnergyUnits == ''

    def test_no_energy_units_found(self):
        """Tests that the EnergyUnits attribute is set to 'keV' if not found in the header."""
        ebounds = RmfEbounds()
        ebounds.read('data/rmf_no_energy_units.rmf')
        assert ebounds.EnergyUnits == 'keV'

    def test_read_method_raises_exception_file_not_found(self):
        """Tests that the read method raises an exception if the file does not exist."""
        rmf_ebounds = RmfEbounds()
        with pytest.raises(FileNotFoundError):
            rmf_ebounds.read('data/nonexistent.rmf')

    def test_read_method_raises_exception_ebounds_not_found(self):
        """Tests that the read method raises an exception if the EBOUNDS extension is not found."""
        rmf_ebounds = RmfEbounds()
        with pytest.raises(KeyError):
            rmf_ebounds.read('data/rmf_no_ebounds.rmf')
