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


class User(object):
    """Class structure to contain the input and output parameters of the user function. """

    # Input parameters:

    #: Number of input parameters from SPEX
    npar = 0
    #: Array containing the parameter values from SPEX (length npar)
    par = None
    #: Number of bins in the input energy grid from SPEX
    neg = 0
    #: Upper boundaries of the energy bins (length neg)
    egb = None
    #: Bin centroids of the energy bins (length neg)
    eg = None
    #: Bin widths of the energy bins (length deg)
    deg = None

    # Output parameters:

    #: Spectrum or transmission (e.g. in ph/s/bin)
    sener = None
    #: If Delta E = average photon energy within the bin (keV) minus the bin centroid then wener = sener * Delta E
    wener = None

    # Filenames:

    #: Input file name
    fprm = None
    #: Output file name
    fspc = None

    def __init__(self):
        """Read the input file names from command line. Then read in the input parameters 
        and energy grid from the SPEX provided input file."""

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
