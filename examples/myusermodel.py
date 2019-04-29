#!/usr/bin/env python

import math  # Import math module
import numpy  # Import numpy module
from pyspextools.model import User  # Import user from pyspextools.model


def main():
    # Initialize the user class. The input file from SPEX will be read automatically.
    usr = User()

    # For each energy bin in the provided energy grid
    # calculate the spectrum in photons/s/bin:
    for i in numpy.arange(usr.neg):
        usr.sener[i] = 1. - usr.par[0] * math.exp(-usr.eg[i])
        usr.wener[i] = 0.

    # Write the calculated spectrum to the output file: 
    usr.write_spc()


main()
