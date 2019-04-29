#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import os
import numpy as np
import pyspextools.messages as message

from .region import Region
from .res import Res
from .spo import Spo
from .pha2 import Pha2
from .pha import Pha
from .rmf import Rmf
from .arf import Arf
from .convert import rmf_to_res
from .convert import pha_to_spo

standard_library.install_aliases()


class TGRegion(Region):
    """The TGRegion class contains methods to read Chandra grating data into the pyspextools module and convert
    these to spo and res format objects."""

    def __init__(self):

        Region.__init__(self)

        self.grating = ''   #: Grating name

    # -----------------------------------------------------
    # Read a set of Chandra grating files into a region
    # -----------------------------------------------------

    def read_region(self, pha2file, rmflist, arflist, grating, bkgsubtract=True):
        """Add a Chandra spectrum and response to a SPEX region. The pha2 file and the rmf and arf file lists
        are mandatory. The grating option can be either HETG, METG or LETG"""

        self.grating = grating

        # Read the PHA2 file for a particular grating
        (src, bkg) = self.__read_pha2(pha2file, grating, bkgsubtract=bkgsubtract)
        if not isinstance(src,Pha):
            message.error("Failed to read spectrum file.")
            return 1

        # Convert the PHA2 file to spo

        rmf = Rmf()
        rmf.read(rmflist[0])

        self.spo = pha_to_spo(src, rmf, back=bkg)
        if not isinstance(self.spo,Spo):
            message.error("Failed to convert spectrum file.")
            return 1

        # Convert the responses to res
        self.res = self.__rmflist_to_res(rmflist, arflist)
        if not isinstance(self.res,Res):
            message.error("Failed to combine and convert response files.")
            return 1

        self.label = grating

        return 0


    def __read_pha2(self, pha2file, grating, bkgsubtract=True):
        # Initialize PHA2 file type

        spec = Pha2()

        # Is the source spectrum there?
        message.proc_start("Read source spectrum")
        if os.path.isfile(pha2file):
            stat = spec.read(pha2file,background=bkgsubtract)
            if stat != 0:
                message.proc_end(stat)
                message.error("Failed to read source spectrum.")
                return 1
            else:
                message.proc_end(stat)
        else:
            message.proc_end(1)
            message.error("Spectrum file {0} not found in path.".format(pha2file))
            return 1

        # Convert grating name to number
        if grating == 'HETG':
            ngrating = 1
        elif grating == 'METG':
            ngrating = 2
        elif grating == 'LETG':
            ngrating = 3
        else:
            message.error("Unsupported grating: '{0}'.".format(grating))
            return 1

        # Combine spectra from a single grating
        message.proc_start("Combining orders of the spectrum")
        (src, bkg) = spec.combine_orders(ngrating)
        if isinstance(src, Pha) and isinstance(bkg, Pha):
            message.proc_end(0)
        else:
            message.proc_end(1)
            return 1

        return src, bkg

    # -----------------------------------------------------
    # Return a res object derived from Chandra grating data
    # -----------------------------------------------------

    def __rmflist_to_res(self, rmflist, arflist):
        """Convert a list of compatible rmf and arf file into one res file. This is convenient for combining responses
        that are provided separately, like the Transmission Grating spectra from Chandra."""

        if len(rmflist) != len(arflist):
            message.error("ARF list and RMF list do not have the same length.")
            return 0

        rmfobjs = np.zeros(len(rmflist), dtype=object)
        arfobjs = np.zeros(len(arflist), dtype=object)
        rmf_orders = np.zeros(len(rmflist), dtype=int)
        arf_orders = np.zeros(len(arflist), dtype=int)

        i = 0
        for file in rmflist:
            message.proc_start("Reading response for order")
            rmf = Rmf()
            rmf.read(file)
            rmf_orders[i] = rmf.Order
            print(str(rmf_orders[i])+"  ", end='')
            if len(np.where(rmf_orders == rmf.Order)) != 1:
                message.error("There are two response files with the same order.")
                message.proc_end(1)
                return 1
            else:
                rmfobjs[i] = rmf
                message.proc_end(0)
            i = i + 1

        i=0
        for file in arflist:
            message.proc_start("Reading effective area for order")
            arf = Arf()
            arf.read(file)
            arf_orders[i] = arf.Order
            print(str(arf_orders[i])+"  ", end='')
            if len(np.where(arf_orders == arf.Order)) != 1:
                message.error("There are two effective area files for the same order.")
                message.proc_end(1)
                return 1
            else:
                arfobjs[i] = arf
                message.proc_end(0)
            i = i + 1

        arfsort = np.argsort(arf_orders)
        rmfsort = np.argsort(rmf_orders)

        # Calculate first response:
        res = rmf_to_res(rmfobjs[rmfsort[0]],arf=arfobjs[arfsort[0]])

        # Append the components from the other responses
        for i in np.arange(len(rmfsort)-1)+1:
            restmp = rmf_to_res(rmfobjs[rmfsort[i]],arf=arfobjs[arfsort[i]])
            res.append_component(restmp)

        return res

