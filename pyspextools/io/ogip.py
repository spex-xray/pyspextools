#!/usr/bin/env python

import pyspextools.messages as message
import numpy as np

from .region import Region
from .res import Res
from .spo import Spo
from .pha import Pha
from .rmf import Rmf
from .arf import Arf
from .convert import pha_to_spo
from .convert import rmf_to_res


class OGIPRegion(Region):
    """The OGIPRegion class contains methods to read OGIP data into the pyspextools module and convert these to
    spo and res format objects.

    :ivar spec: Input PHA source spectrum.
    :vartype spec: pyspextools.io.pha.Pha
    :ivar back: Input PHA background spectrum (optional).
    :vartype back: pyspextools.io.pha.Pha
    :ivar resp: Input RMF response matrix.
    :vartype resp: pyspextools.io.rmf.Rmf
    :ivar area: Input ARF effective area (optional).
    :vartype area: pyspextools.io.arf.Arf
    :ivar corr: Input CORR correction file (optional).
    :vartype corr: pyspextools.io.pha.Pha

    :ivar input_spec: Is a source spectrum read in?
    :vartype input_spec: bool
    :ivar input_back: Is a background spectrum specified?
    :vartype input_back: bool
    :ivar input_resp: Is a response matrix read in?
    :vartype input_resp: bool
    :ivar input_area: Is an effective area file specified?
    :vartype input_area: bool
    :ivar input_corr: Is a correction file specified?
    :vartype input_corr: bool

    :ivar first_channel_zero: If the first channel is 0, then matrix data needs shift since SPEX starts at 1.
    :vartype first_channel_zero: bool
    :ivar save_grouping: Save the grouping of the spectra (Default: no).
    :vartype save_grouping: bool
    """

    def __init__(self):

        Region.__init__(self)

        self.spec = Pha()  # Input PHA source spectrum.
        self.back = Pha()  # Input PHA background spectrum (optional).
        self.resp = Rmf()  # Input RMF response matrix.
        self.area = Arf()  # Input ARF effective area (optional).
        self.corr = Pha()  # Input CORR correction file (optional).

        self.input_spec = False  # Is a source spectrum read in?
        self.input_back = False  # Is a background spectrum specified?
        self.input_resp = False  # Is a response matrix read in?
        self.input_area = False  # Is an effective area file specified?
        self.input_corr = False  # Is a correction file specified?

        self.first_channel_zero = False  # If the first channel is 0, then matrix data needs shift.
        self.save_grouping = False       # By default no grouping of data

    # -----------------------------------------------------
    # Read a set of OGIP files into a region
    # -----------------------------------------------------

    def read_region(self, phafile, rmffile, bkgfile=None, arffile=None, corrfile=None, grouping=False):
        """Add an OGIP spectrum and response to a SPEX region. The pha and rmf file names
        are mandatory. If needed, a background file and effective area file can be added.

        :param phafile: Name of the PHA file to read.
        :type phafile: str
        :param rmffile: Name of the RMF file to read.
        :type rmffile: str
        :param bkgfile: Name of the background PHA file to read (optional).
        :type bkgfile: str
        :param arffile: Name of the ARF file to read (optional).
        :type arffile: str
        :param corrfile: Name of the Correction file to read (optional).
        :type corrfile: str
        :param grouping: Keep the grouping information?
        :type grouping: bool
        """

        # Read the source PHA file
        self.read_source_pha(phafile)

        # Read the background PHA file if specified:
        if bkgfile is not None:
            self.read_background_pha(bkgfile)

        # Read a correction spectrum if specified:
        if corrfile is not None:
            self.read_corr(corrfile)

        # Read the response matrix
        self.read_rmf(rmffile)

        # Read the effective area
        if arffile is not None:
            self.read_arf(arffile)

        # Should the spectrum grouping remain?
        self.save_grouping = grouping

        if not self.input_back:
            self.back = None

        if not self.input_corr:
            self.corr = None

        if not self.input_area:
            self.area = None
        
        # Do the OGIP to SPEX conversion
        stat = self.ogip_to_spex()
        if stat != 0:
            message.error("OGIP to spex conversion failed.")
            return 1

    # -----------------------------------------------------
    # Add OGIP objects to the OGIP region and convert
    # -----------------------------------------------------

    def add_region(self, spec, resp, back=None, corr=None, area=None):
        """Add OGIP objects to an OGIP region. This is useful when the OGIP files are already read in, but they
        need to be added to an OGIP region and converted to spo and res objects.

        :param spec: PHA object to add.
        :type spec: pyspextools.io.pha.Pha
        :param resp: RMF object to add.
        :type resp: pyspextools.io.rmf.Rmf
        :param back: PHA background object to add.
        :type back: pyspextools.io.pha.Pha
        :param corr: PHA correction spectrum to add.
        :type corr: pyspextools.io.pha.Pha
        :param area: ARF effective area object to add.
        :type area: pyspextools.io.arf.Arf
        """

        # Load Pha object
        if isinstance(spec, Pha):
            self.spec = spec
            self.input_spec = True
        else:
            message.error("Input spectrum object is not of type Pha.")
            return 1

        # Load Rmf object
        if isinstance(resp, Rmf):
            self.resp = resp
            self.input_resp = True
        else:
            message.error("Input response object is not of type Rmf.")
            return 1

        # Load background object (if available)
        if isinstance(back, Pha):
            self.back = back
            self.input_back = True
        elif back is None:
            self.input_back = False
        else:
            self.input_back = False
            message.error("Input background object is not of type Pha.")
            return 1

        # Load correction spectrum (if available)
        if isinstance(corr, Pha):
            self.corr = corr
            self.input_corr = True
        elif corr is None:
            self.input_corr = False
        else:
            self.input_corr = False
            message.error("Input correction object is not of type Pha.")
            return 1

        # Load effective area (if available)
        if isinstance(area, Arf):
            self.area = area
            self.input_area = True
        elif area is None:
            self.input_area = False
        else:
            self.input_area = False
            message.error("Input effective area object is not of type Arf.")
            return 1

        # Do the OGIP to SPEX conversion
        stat = self.ogip_to_spex()
        if stat != 0:
            message.error("OGIP to spex conversion failed.")
            return 1

        return 0

    # -----------------------------------------------------
    # Convert the OGIP part of the region to spo and res
    # -----------------------------------------------------

    def ogip_to_spex(self):
        """Convert the OGIP part of the OGIP region to spo and res objects."""

        # Check the consistency between the OGIP files
        stat = self.check_ogip()
        if stat != 0:
            message.error("Check of OGIP files failed.")
            return 1

        # Convert OGIP spectra to SPO object:
        if self.input_spec and self.input_resp:
            message.proc_start("Convert OGIP spectra to spo format")
            spo = pha_to_spo(self.spec, self.resp, back=self.back, corr=self.corr, save_grouping=self.save_grouping)

            if isinstance(spo, Spo):
                self.spo = spo
                message.proc_end(0)
            else:
                message.proc_end(1)
                message.error("OGIP to SPO failed.")
                return 1

            message.proc_start("Convert OGIP response to res format")
            res = rmf_to_res(self.resp, matext=0, arf=self.area)
            if self.resp.NumberMatrixExt > 1:
                for i in range(self.resp.NumberMatrixExt-1):
                    rescomp = rmf_to_res(self.resp, matext=i+1, arf=self.area)
                    res.append_component(rescomp, iregion=1, isector=1)

            if isinstance(res, Res):
                self.res = res
                message.proc_end(0)
            else:
                message.error("OGIP to RES failed.")
                return 1
        else:
            message.error("Source spectrum or response not specified.")
            return 1

        # Correct for possible shifts in channels if first channel is 0
        if self.resp.ebounds.FirstChannel == 0:
            for i in range(self.resp.NumberMatrixExt):
                self.correct_possible_shift(i)

        # Check output spo object
        checkspo = self.spo.check()
        if checkspo != 0:
            message.error("Resulting spo file is not OK.")
            return 1

        # Check
        checkres = self.res.check()
        if checkres != 0:
            message.error("Resulting res file is not OK.")
            return 1

        return 0

    # -----------------------------------------------------
    # Read an OGIP pha file
    # -----------------------------------------------------

    def read_source_pha(self, phafile):
        """Open a pha file containing the source spectrum.

        :param phafile: PHA file name of source spectrum to read.
        :type phafile: str
        """

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

    def read_background_pha(self, bkgfile):
        """Open a pha file containing the background spectrum (if specified).

        :param bkgfile: PHA file name of background spectrum to read.
        :type bkgfile: str
        """

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

    def read_rmf(self, rmffile):
        """Open rmf file containing the response matrix.

        :param rmffile: RMF file name to read.
        :type rmffile: str
        """
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

    def read_arf(self, arffile):
        """Read arf file containing the effective area.

        :param arffile: ARF file name to read.
        :type arffile: str
        """

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

    def read_corr(self, corrfile):
        """Read correction file if specified.

        :param corrfile: PHA correction file name to read.
        :type corrfile: str
        """

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
    # Check for possible shifts in response array
    # -----------------------------------------------------
    def correct_possible_shift(self, ext):
        """See if there is a shift in the response array. When the spectral channels start at 0 in OGIP responses,
        then there is a possibility that the channel indexing needs to be shifted by 1. The SPEX format first
        channel should always be 1. Run this function after the conversion of OGIP to SPEX had taken place
        and if the first channel in the OGIP spectrum is 0.
        The ogip_to_spex method calls this function by default.

        :param ext: Matrix extension number (Most RMFs have only one extension (ext=0), but could be more)
        :type ext: int
        """

        if not isinstance(self.spo, Spo) or not isinstance(self.res, Res):
            message.error("Could not find spo and res information in this region.")
            return 1

        # This code is not prepared for situations where the channel arrays are swapped, like for RGS.
        # Luckily, the combination of a 0 first channel and a swapped array are rare.
        # In that case, we stop with a warning:
        if self.spo.swap:
            message.warning("Not auto-detecting shifts in the response array. ")
            return 1

        # Check the channel range in the res file. Are the first channels starting at 0 as well?
        # Is the last channel larger than the given channel number? Then the ic1 and ic2 channels may
        # actually be mapped on a grid starting with 1.
        min_ic1 = np.amin(self.res.ic1)
        max_ic2 = np.amax(self.res.ic2)

        if (min_ic1 == 1 and max_ic2 == np.amax(self.resp.ebounds.Channel)+1):
            # The actual mapping appears to be on a grid starting at 1.
            # We can ignore the channel numbers in ebounds and proceed without a shift
            print("No shift in response array detected. Continuing...")
            return

        # Check the OGIP response object
        # Check the channel indices for the first group with useful data
        # Find such a group first in OGIP response:
        i = 0
        while True:
            # Find an energy bin with at least one response group.
            if self.resp.matrix[ext].NumberGroups[i] == 0:
                i = i + 1
            else:
                break

        # Save the energy boundaries and calculate the average model energy for the group
        elow = self.resp.matrix[ext].LowEnergy[i]
        ehigh = self.resp.matrix[ext].HighEnergy[i]
        target_energy = (elow + ehigh) / 2.0

        # For this group, save the first channel of the group (F_CHAN)
        fchan = self.resp.matrix[ext].FirstChannelGroup[i]

        # Find the array index for this channel number
        j = 0
        while True:
            if self.resp.ebounds.Channel[j] != fchan:
                j = j + 1
            else:
                break

        # For this array index, the corresponding channel energy boundaries should be:
        lchan = self.resp.ebounds.ChannelLowEnergy[j]
        hchan = self.resp.ebounds.ChannelHighEnergy[j]
        target_channel = (lchan + hchan) / 2.0

        # Now find the same group and channel in the SPEX format objects
        # Find the group in the res object for the same model energy bin (with target_energy):
        s = 0
        while True:
            if self.res.eg1[s] < target_energy and self.res.eg2[s] > target_energy:
                break
            else:
                s = s + 1

        # Find the target channel number in spo file
        t = 0
        while True:
            if self.spo.echan1[t] < target_channel and self.spo.echan2[t] > target_channel:
                break
            else:
                t = t + 1

        # Corresponding first channel of this group according to SPEX format
        ic1 = self.res.ic1[s]

        # Calculate the difference between the SPEX channel number and the OGIP one.
        shift = int(t + 1 - ic1)

        if shift != 0:
            message.warning("Shift in response array detected.")
            message.proc_start("Trying to shift indices with {0} ".format(shift))
            stat = self.res.channel_shift(shift)
            message.proc_end(stat)
        else:
            print("No shift in response array detected. Continuing...")

        return 0

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
            back = self.spec.check_compatibility(self.back)
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
            corr = self.spec.check_compatibility(self.corr)
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
            area = self.resp.check_compatibility(self.area)
            if area != 0:
                message.proc_end(1)
                message.error("Effective area file is not consistent with the provided response file.")
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
