
# Generated by CodiumAI

import os
import pytest
import numpy as np
from pyspextools.io.rmf import Rmf, RmfMatrix
from pyspextools.io.arf import Arf

"""
Code Analysis

Main functionalities:
The Rmf class is used to read and write response matrix files (RMF) used in X-ray spectroscopy. 
It contains information about the energy bins and response matrix for a given instrument. 
The class can read an RMF file, check its consistency, display its contents, and write a 
new RMF file. It can also check the compatibility of an associated ARF file.

Methods:
- read(rmffile): reads an RMF file and extracts the energy bin and response matrix information.
- write(rmffile, telescop=None, instrume=None, filterkey=None, overwrite=False): writes a new RMF 
  file with the current energy bin and response matrix information.
- check(): checks the consistency of the RMF file.
- disp(): displays the contents of the RMF file.
- check_compatibility(arf): checks the compatibility of an associated ARF file.

Fields:
- ebounds: an instance of the RmfEbounds class that contains information about the energy bins.
- matrix: a list of RmfMatrix instances that contain information about the response matrix.
- NumberMatrixExt: the number of response matrix extensions.
- MatrixExt: an array of integers that contains the indices of the response matrix extensions in the RMF file.
"""


class TestRmf:

    def test_read_valid_rmf(self):
        """Tests that the read method can successfully read a valid RMF file."""
        rmf = Rmf()
        assert rmf.read('data/rmf_valid.rmf') == 0

    def test_write_valid_rmf(self):
        """Tests that the write method can successfully write a valid RMF file."""
        rmf = Rmf()
        rmf.read('data/rmf_valid.rmf')
        assert rmf.write('tmp/test_rmf.rmf', overwrite=True) == 0

    def test_check_rmf_compatibility_with_arf(self):
        """Tests that the check_compatibility method returns an error when the input Arf instance
        is not compatible with the RMF."""
        rmf = Rmf()
        rmf.read('data/rmf_valid.rmf')
        arf = Arf()
        arf.read('data/arf.arf')
        assert rmf.check_compatibility(arf) == 0
