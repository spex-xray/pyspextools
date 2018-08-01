#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import pyspex.messages as message

from .region import Region
from .res import Res
from .spo import Spo
from .pha import Pha
from .rmf import Rmf
from .arf import Arf
from .convert import pha_to_spo
from .convert import rmf_to_res

standard_library.install_aliases()


class OGIPRegion(Region):
    """The OGIPRegion class contains methods to read OGIP data into the pyspex module and convert these to spo and res
    format objects."""

    def __init__(self):

        Region.__init__(self)

        self.spec = Pha()  #: Input PHA source spectrum.
        self.back = Pha()  #: Input PHA background spectrum (optional).
        self.resp = Rmf()  #: Input RMF response matrix.
        self.area = Arf()  #: Input ARF effective area (optional).
        self.corr = Pha()  #: Input CORR correction file (optional).

        self.input_spec = False  #: Is a source spectrum read in?
        self.input_back = False  #: Is a background spectrum specified?
        self.input_resp = False  #: Is a response matrix read in?
        self.input_area = False  #: Is an effective area file specified?
        self.input_corr = False  #: Is a correction file specified?

        self.first_channel_zero = False  #: If the first channel is 0, then matrix data needs shift since SPEX starts at 1.
        self.save_grouping = False  #: By default no grouping of data

    # -----------------------------------------------------
    # Read a set of OGIP files into a region
    # -----------------------------------------------------

    def read_region(self, phafile, rmffile, bkgfile=None, arffile=None, corrfile=None, grouping=False):
        """Add an OGIP spectrum and response to a SPEX region. The pha and rmf file names
        are mandatory. If needed, a background file and effective area file can be added."""

        # Read the source PHA file
        self.__read_source_pha(phafile)

        # Read the background PHA file if specified:
        if bkgfile is not None:
            self.__read_background_pha(bkgfile)

        # Read a correction spectrum if specified:
        if corrfile is not None:
            self.__read_corr(corrfile)

        # Read the response matrix
        self.__read_rmf(rmffile)

        # Read the effective area
        if arffile is not None:
            self.__read_arf(arffile)

        # Should the spectrum grouping remain?
        self.save_grouping = grouping

        # Check the consistency between the OGIP files
        stat = self.check_ogip()
        if stat != 0:
            message.error("Check of OGIP files failed.")
            return

        if not self.input_back:
            self.back = None

        if not self.input_corr:
            self.corr = None

        if not self.input_area:
            self.area = None

        # Convert OGIP spectra to SPO object:
        if self.input_spec and self.input_resp:
            message.proc_start("Convert OGIP spectra to spo format")
            spo = pha_to_spo(self.spec,self.resp,back=self.back,corr=self.corr)

            if isinstance(spo,Spo):
                self.spo = spo
                message.proc_end(0)
            else:
                message.proc_end(1)
                message.error("OGIP to SPO failed.")
                return

            message.proc_start("Convert OGIP response to res format")
            res = rmf_to_res(self.resp,arf=self.area)

            if isinstance(res,Res):
                self.res = res
                message.proc_end(0)
            else:
                message.error("OGIP to RES failed.")
                return
        else:
            message.error("Source spectrum or response not specified.")
            return

        # Check output spo object
        checkspo = self.spo.check()
        if checkspo != 0:
            message.error("Resulting spo file is not OK.")
            return

        # Check
        checkres = self.res.check()
        if checkres != 0:
            message.error("Resulting res file is not OK.")
            return

    # -----------------------------------------------------
    # Read an OGIP pha file
    # -----------------------------------------------------

    def __read_source_pha(self, phafile):
        """Open a pha file containing the source spectrum."""
        message.proc_start("Read source PHA spectrum")
        stat = self.spec.read(phafile)
        if stat != 0:
            message.proc_end(stat)
            message.error("Unable to read source PHA file.")
            return
        else:
            self.input_spec = True
            message.proc_end(stat)

        # Check if first channel of spectrum is zero:
        if self.spec.FirstChannel == 0:
            self.first_channel_zero = True
        else:
            self.first_channel_zero = False

    # -----------------------------------------------------
    # Read an OGIP background file
    # -----------------------------------------------------

    def __read_background_pha(self, bkgfile):
        """Open a pha file containing the background spectrum (if specified)."""
        if bkgfile is not None:
            message.proc_start("Read background PHA spectrum")
            stat = self.back.read(bkgfile)
            if stat != 0:
                message.proc_end(stat)
                message.error("Unable to read background PHA file.")
                return
            else:
                self.input_back = True
                message.proc_end(stat)
        else:
            message.error("No background filename specified.")

    # -----------------------------------------------------
    # Read an OGIP rmf file
    # -----------------------------------------------------

    def __read_rmf(self, rmffile):
        """Open rmf file containing the response matrix."""
        message.proc_start("Read RMF response matrix")
        stat = self.resp.read(rmffile)
        if stat != 0:
            message.proc_end(stat)
            message.error("Unable to read RMF/RSP file.")
            return
        else:
            self.input_resp = True
            message.proc_end(stat)

    # -----------------------------------------------------
    # Read an OGIP arf file
    # -----------------------------------------------------

    def __read_arf(self, arffile):
        """Read arf file containing the effective area."""
        if arffile is not None:
            message.proc_start("Read ARF effective area")
            stat = self.area.read(arffile)
            if stat != 0:
                message.proc_end(stat)
                message.error("Unable to read ARF file.")
                return
            else:
                self.input_area = True
                message.proc_end(stat)
        else:
            message.error("No effective area filename specified.")

    # -----------------------------------------------------
    # Read an OGIP corr file
    # -----------------------------------------------------

    def __read_corr(self, corrfile):
        """Read correction file if specified."""
        if corrfile is not None:
            message.proc_start("Read correction spectrum")
            stat = self.corr.read(corrfile)
            if stat != 0:
                message.proc_end(stat)
                message.error("Unable to read CORR file.")
                return
            else:
                message.proc_end(stat)
                self.input_corr = True
        else:
            message.error("No correction file specified.")

    # -----------------------------------------------------
    # Do a consistency check for the OGIP part
    # -----------------------------------------------------

    def check_ogip(self):
        """Check consistency of the OGIP files in this class."""

        # Check consistency of the source spectrum
        message.proc_start("Check OGIP source spectrum")

        spec = self.spec.check()

        if spec != 0:
            message.proc_end(1)
            print(spec)
            return 1
        else:
            message.proc_end(0)

        # Check consistency of the background spectrum
        if self.input_back:
            # Is the background file in order?
            message.proc_start("Check OGIP background spectrum")
            back = self.back.check()
            if back != 0:
                message.proc_end(1)
                print(back)
                return 1
            back = self.spec.checkCompatibility(self.back)
            if back != 0:
                message.proc_end(1)
                message.error("Background spectrum is not compatible with source spectrum.")
                return 1
            message.proc_end(0)

        # Check consistency of the correction spectrum
        if self.input_corr:
            # Is the correction file in order?
            message.proc_start("Check OGIP correction spectrum")
            corr = self.corr.check()
            if corr != 0:
                message.proc_end(1)
                print(corr)
                return 1
            corr = self.spec.checkCompatibility(self.corr)
            if corr != 0:
                message.proc_end(1)
                message.error("Correction spectrum is not compatible with source spectrum.")
                return 1
            message.proc_end(0)

        # Check rmf file
        message.proc_start("Check OGIP response matrix")
        resp = self.resp.check()
        if resp != 0:
            message.proc_end(1)
            print(resp)
            return 1
        message.proc_end(0)

        # Check consistency between ARF and RMF
        if self.input_area:
            # Is the effective area file in order?
            message.proc_start("Check OGIP effective area file")
            area = self.area.check()
            if area != 0:
                message.proc_end(1)
                print(area)
                return 1
            # Is the effective area consistent with the response?
            area = self.resp.checkCompatibility(self.area)
            if area != 0:
                message.proc_end(1)
                print("Error: Effective area file is not consistent with the provided response file.")
                return 1
            message.proc_end(0)

        return 0

    # -----------------------------------------------------
    # Show a summary of the provided OGIP data
    # -----------------------------------------------------

    def show_ogip(self):
        """Shows a summary of the loaded OGIP data."""

        print("===========================================================")
        print("Summary of OGIP information:")
        print("===========================================================")

        self.spec.disp()

        if self.input_back:
            self.back.disp()
        else:
            print("No background spectrum provided.")
            print("")

        if self.input_corr:
            self.corr.disp()
        else:
            print("No correction spectrum provided.")
            print("")

        self.resp.disp()

        if self.input_area:
            self.area.disp()
        else:
            print("No effective area file provided.")
            print("")

        print("===========================================================")

