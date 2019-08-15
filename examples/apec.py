#!/usr/bin/env python

"""
This example program creates an interface between ATOMDB and
the SPEX user model. Using this program, the APEC model can be used
within SPEX.

This model needs the pyatomdb module from atomdb.org and numpy.
Also set the ATOMDB environment variable to a local ATOMDB installation.
"""

# Stuff to import for compatibility between python 2 and 3
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library

import sys
import numpy
from pyspextools.model import User

standard_library.install_aliases()

try:
    import pyatomdb
except ImportError:
    print("This SPEX user model depends on the pyATOMDB module. Please install"
          "pyATOMDB through the command 'pip install pyatomdb'. ")
    print("Note that from version 0.6.0 onwards pyATOMDB only supports Python 3.")

"""
User model parameter translation table:
p01	usr.par[0]	Normalisation Photons m^-3 s^-1 keV^-1
p02	usr.par[1]	Temperature in keV
p03  	usr.par[2]	-
p04	usr.par[3]	-
p05	usr.par[4]	-
p06	usr.par[5]	06 C
p07	usr.par[6]	07 N
p08	usr.par[7]	08 O
p09 	usr.par[8]	09 F
p10	usr.par[9]	10 Ne
p11	usr.par[10]	11 Na
p12	usr.par[11]	12 Mg
p13	usr.par[12]	13 Al
p14	usr.par[13]	14 Si
p15	usr.par[14]	15 P
p16	usr.par[15]	16 S
p17	usr.par[16]	17 Cl
p18	usr.par[17]	18 Ar
p19	usr.par[18]	19 K
p20	usr.par[19]	20 Ca
p21	usr.par[20]	21 Sc
p22	usr.par[21]	22 Ti
p23	usr.par[22]	23 V
p24	usr.par[23]	24 Cr
p25	usr.par[24]	25 Mn
p26	usr.par[25]	26 Fe
p27	usr.par[26]	27 Co
p28	usr.par[27]	28 Ni
p29	usr.par[28]	29 Cu
p30	usr.par[29]	30 Zn
"""


def main():
    # Initialize the IO class. The input file from SPEX will be read automatically.
    usr = User()

    if usr.npar != 30:
        print("Please set 'npar' parameter to 30 for this model")
        sys.exit()

    # Create a pyatomdb spectrum session
    data = pyatomdb.spectrum.Session()

    # Set the energy grid for the calculation
    # Pyatomdb expects bin boundaries (n+1)
    # SPEX has an array of upper boundary,
    # so we need to calculate the lower boundary
    # for the first bin:
    fbin = numpy.array([usr.egb[0] - usr.deg[0]])

    # And set the energy bins
    data.set_specbins(numpy.append(fbin, usr.egb), specunits='keV')

    # Set abundance table
    data.set_abundset("AG89")  # Anders & Grevesse (1989)

    # Set atomic number array
    atom = numpy.arange(30) + 1

    # Set model parameters
    norm = 1E+14 * usr.par[0]  # Photons cm^-3 s^-1 keV^-1
    # APEC norm is 1E-14 times emission measure
    temp = usr.par[1]  # Temperature in keV

    # Parameters with index 2,3,4 are not used

    # Set abundances for C to Zn    
    for a in numpy.arange(25) + 5:
        data.set_abund(atom[a], usr.par[a])

    # Calculate the APEC spectrum
    aspec = data.return_spectra(temp, teunit='keV')

    # Write the calculated spectrum to the sener array:
    for i in numpy.arange(usr.neg):
        usr.sener[i] = norm * aspec[i]

    # Write the calculated spectrum to the output file: 
    usr.write_spc()


main()
