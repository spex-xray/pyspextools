#!/usr/bin/env python

import math                    # Import math module
import numpy                   # Import numpy module
from pyspex.model import user  # Import user from pyspex.model


def main():
    # Initialize the user class. The input file from SPEX will be read automatically.
    usr=user()
    
    # For each energy bin in the provided energy grid
    # calculate the spectrum in photons/s/bin:
    for i in numpy.arange(usr.neg):
      usr.sener[i]=1.- usr.par[0]*math.exp(-usr.eg[i])
      usr.wener[i]=0.
    
    # Write the calculated spectrum to the output file: 
    usr.Writespc()

main()
