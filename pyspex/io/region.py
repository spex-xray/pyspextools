#!/usr/bin/env python

# =========================================================
"""
  Python module to organise SPEX res and spo files into regions.
  See this page for the format specification:

    http://var.sron.nl/SPEX-doc/manualv3.04/manualse108.html#x122-2840008.2

  This module contains the Region class:

    Region:    Contains the the combination of a spectrum and a
               response organized in a SPEX region

  Dependencies:
    - numpy:      Array operations
    - spo:        The spo class from this pyspex data module
    - res:        The res class from this pyspex data module
"""
# =========================================================


# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

from pyspex.io.spo import Spo
from pyspex.io.res import Res

standard_library.install_aliases()


# =========================================================
# Region class
# =========================================================

class Region:
    """A SPEX region is a spectrum/response combination for a
       specific observation, instrument or region on the sky.
       It combines the spectrum and response file in one object."""

    def __init__(self):
        self.spo = Spo()
        self.res = Res()

    def check(self):
        """Check whether spectrum and response are compatible
           and whether the arrays really consist of one region."""
        pass

    def show(self):
        """Show a summary of the region metadata."""

        print("===========================================================")
        print(" Sector:             " + str(self.res.sector[0]))
        print(" Region:             " + str(self.res.region[0]))

        print(" --------------------  Spectrum  -------------------------")
        self.spo.show()

        print(" --------------------  Response  -------------------------")
        self.res.show(iregion=self.res.region[0])

