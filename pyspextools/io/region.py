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
    - spo:        The spo class from this pyspextools data module
    - res:        The res class from this pyspextools data module
"""
# =========================================================


# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import numpy as np

from pyspextools.io.spo import Spo
from pyspextools.io.res import Res
import pyspextools.messages as message

standard_library.install_aliases()


# =========================================================
# Region class
# =========================================================

class Region:
    """A SPEX region is a spectrum/response combination for a
       specific observation, instrument or region on the sky.
       It combines the spectrum and response file in one object."""

    def __init__(self):
        self.spo = Spo()        #: Spo object
        self.res = Res()        #: Res object
        self.label = ""         #: Optional region label (will not be written to file). For example: MOS1, annulus2, etc.

    def change_label(self, label):
        """Attach a label to this region to easily identify it. For example: MOS1, annulus 2, etc."""
        self.label = str(label)

    def set_sector(self,sector):
        """Set the sector number for this region."""

        for i in np.arange(self.res.sector.size):
            self.res.sector[i]=sector


    def check(self, nregion=False):
        """Check whether spectrum and response are compatible
           and whether the arrays really consist of one region (if nregion flag is set)."""

        if self.res.nchan[0] != self.spo.nchan[0]:
            message.error("Number of channels in spectrum is not equal to number of channels in response.")
            return -1

        if nregion:
            if self.spo.nchan.size != 1:
                message.error("SPO object consists of more than one region according to nchan array size.")
                return -1

            if self.spo.nregion != 1:
                message.error("SPO object consists of more than one region according to nregion parameter.")
                return -1

        return 0

    def show(self,isector=1,iregion=1):
        """Show a summary of the region metadata."""

        print("===========================================================")
        print(" Sector:            {0}  =>  Region:            {1}".format(str(self.res.sector[0]),
              str(self.res.region[0])))
        print(" Label:             {0}".format(self.label))

        print(" --------------------  Spectrum  -------------------------")
        self.spo.show()

        print(" --------------------  Response  -------------------------")
        self.res.show(isector=isector,iregion=iregion)

