#!/usr/bin/env python

"""This is a module containing the necessary methods to
develop an executable for use with the SPEX user model.
"""

# Stuff to import for compatibility between python 2 and 3
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import open
from builtins import str
from future import standard_library

from builtins import object

import sys
import math
import numpy

standard_library.install_aliases()


class User:
    """Class structure to contain the input and output parameters of the user function.

    :ivar npar: Numper of model input parameters from SPEX.
    :vartype npar: int
    :ivar par: Array containing the parameter values from SPEX (length npar).
    :vartype par: numpy.ndarray
    :ivar neg: Number of bins in the input energy grid from SPEX.
    :vartype neg: int
    :ivar egb: Upper boundaries of the energy bins (length neg).
    :vartype egb: numpy.ndarray
    :ivar eg: Bin centroids of the energy bins (length neg).
    :vartype eg: numpy.ndarray
    :ivar deg: Bin widths of the energy bins (length deg).
    :vartype deg: numpy.ndarray

    :ivar sener: Spectrum or transmission (e.g. in ph/s/bin)
    :vartype sener: numpy.ndarray
    :ivar wener: If Delta E = average photon energy within the bin (keV) minus the bin centroid then wener = sener * Delta E
    :vartype wener: numpy.ndarray

    :ivar fprm: Input file name from command line.
    :vartype fprm: str
    :ivar fspc: Output file name from command line.
    :vartype fspc: str
    """

    def __init__(self):
        """Read the input file names from command line. Then read in the input parameters 
        and energy grid from the SPEX provided input file."""

        # Input parameters:
        self.npar = 0                              # Number of input parameters from SPEX
        self.par = numpy.array([], dtype=float)    # Array containing the parameter values from SPEX (length npar)
        self.neg = 0                               # Number of bins in the input energy grid from SPEX
        self.egb = numpy.array([], dtype=float)    # Upper boundaries of the energy bins (length neg)
        self.eg = numpy.array([], dtype=float)     # Bin centroids of the energy bins (length neg)
        self.deg = numpy.array([], dtype=float)    # Bin widths of the energy bins (length deg)

        # Output parameters:
        self.sener = numpy.array([], dtype=float)  # Spectrum or transmission (e.g. in ph/s/bin)
        self.wener = numpy.array([], dtype=float)  # If Delta E = average photon energy within the bin (keV) minus
        # the bin centroid then wener = sener * Delta E

        # Filenames:
        self.fprm = ''        # Input file name
        self.fspc = ''        # Output file name

        self.read_prm()

    def read_prm(self):
        """Read the parameter file that SPEX creates at the beginning of the model evaluation. This is done
        automatically when the User class is initialised."""

        try:
            self.fprm = sys.argv[1]
        except IndexError:
            print(
                "Error: Cannot read input filename from command line.\n Please only use this module in an executable.")
            sys.exit(1)

        try:
            self.fspc = sys.argv[2]
        except IndexError:
            print(
                "Error: Cannot read output filename from command line.\n Please only use this module in an executable.")
            sys.exit(1)

        # Open input file
        try:
            f = open(self.fprm, 'r')
        except IOError:
            print("Error: Input file does not exist...")
            sys.exit(1)

        # Read the number of parameters
        self.npar = int(f.readline())

        # Allocate an array containing the parameters
        self.par = numpy.zeros(self.npar, dtype=float)

        # Read parameters into the array for the parameters
        spar = []
        for _ in numpy.arange(math.ceil(self.npar / 5)):
            spar.append(str(f.readline()).split())

        # Flatten list
        spar = sum(spar, [])

        for i in numpy.arange(self.npar):
            self.par[i] = float(spar[i])

        # Read the number of model grid bins  
        self.neg = int(f.readline())

        # Allocate an array for the energy bin boundary egb, bin center eg, and delta e, deg 
        self.egb = numpy.zeros(self.neg)
        self.eg = numpy.zeros(self.neg)
        self.deg = numpy.zeros(self.neg)

        # Read the energy grid from the input file
        for i in numpy.arange(self.neg):
            row = str(f.readline()).split()
            self.egb[i] = float(row[0])
            self.eg[i] = float(row[1])
            self.deg[i] = float(row[2])

        # Close the file
        f.close()

        # Set size of sener and wener arrays
        self.sener = numpy.zeros(self.neg, dtype=float)
        self.wener = numpy.zeros(self.neg, dtype=float)

    def write_spc(self):
        """Write the calculated spectrum to the output file for SPEX.
        Make sure that the sener and wener arrays are initialized and 
        filled with a spectrum before calling this function."""

        # Do some checks on the sener and wener arrays that should be set.
        if len(self.sener) == 0:
            print("Error: sener array not initialized yet.")
            sys.exit(1)

        if len(self.sener) != self.neg:
            print("Error: sener array has an incorrect size.")
            sys.exit(1)

        if len(self.wener) == 0:
            print("Error: wener array not initialized yet.")
            sys.exit(1)

        if len(self.wener) != self.neg:
            print("Error: wener array has an incorrect size.")
            sys.exit(1)

            # Open the output file
        try:
            f = open(self.fspc, 'w')
        except IOError:
            print("Error: unable to open output file.")
            sys.exit(1)

            # Write the number of model bins to the output file
        f.write(str(self.neg) + '\n')

        # Write the sener and wener columns to the output file
        for i in numpy.arange(self.neg):
            f.write(str(self.sener[i]) + '  ' + str(self.wener[i]) + '\n')

        # Close the file
        f.close()
        return
