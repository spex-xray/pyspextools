#!/usr/bin/env python

import math                  # Import math module
import numpy                 # Import numpy module
from pyspex.user import IO   # Import IO from pyspex.user


def main():
    # Initialize the IO class. The input file from SPEX will be read automatically.
    usr=IO()
    
    # For each energy bin in the provided energy grid
    # calculate the spectrum in photons/s/bin:
    for i in numpy.arange(usr.neg):
      usr.sener[i]=1.- usr.par[0]*math.exp(-usr.eg[i])
      usr.wener[i]=0.
    
    # Write the calculated spectrum to the output file: 
    usr.writespc()

main()
