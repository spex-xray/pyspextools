#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import numpy as np
import math

from .data import Region
from .res import Res
from .spo import Spo

standard_library.install_aliases()

# See if Heasoft python modules are available
try:
    import heasp
except ImportError:
    has_heasp = False
else:
    has_heasp = True


class OGIPRegion(Region):
    """The OGIPRegion class contains methods to read OGIP data into the pyspex module and convert these to spo and res
    format objects."""

    def __init__(self):

        Region.__init__(self)

        if not has_heasp:
            raise ImportError("HEASP module from HEASOFT is required for OGIP functionality.\n "
                              "Please source your local HEASOFT installation to use this module.")

        self.spec = heasp.pha()  #: Input PHA source spectrum.
        self.back = heasp.pha()  #: Input PHA background spectrum (optional).
        self.resp = heasp.rmf()  #: Input RMF response matrix.
        self.area = heasp.arf()  #: Input ARF effective area (optional).
        self.corr = heasp.pha()  #: Input CORR correction file (optional).

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

        # Check the consistency between the OGIP files
        stat = self.check_ogip()
        if stat != 0:
            print("Error: Check of OGIP files failed.")
            return

        # Convert OGIP spectra to SPO object:
        if self.input_spec and self.input_resp:
            spo = self.ogip_to_spo()
            if spo != 0:
                self.spo = spo
            else:
                print("Error: OGIP to SPO failed.")
                return

            res = self.ogip_to_res()
            if res != 0:
                self.res = res
            else:
                print("Error: OGIP to RES failed.")
                return
        else:
            print("Error: Source spectrum or response not specified.")
            return

        # Check output spo object
        checkspo = self.spo.check()
        if checkspo != 0:
            print("Error: Resulting spo file is not OK.")
            return

        # Check
        checkres = self.res.check()
        if checkres != 0:
            print("Error: Resulting res file is not OK.")
            return

    # -----------------------------------------------------
    # Read an OGIP pha file
    # -----------------------------------------------------

    def read_source_pha(self, phafile):
        """Open a pha file containing the source spectrum."""
        stat = self.spec.read(phafile)
        if stat != 0:
            print("Error: Unable to read source PHA file.")
            return
        else:
            self.input_spec = True

        # Check if first channel of spectrum is zero:
        if self.spec.FirstChannel == 0:
            self.first_channel_zero = True
        else:
            self.first_channel_zero = False

    # -----------------------------------------------------
    # Read an OGIP background file
    # -----------------------------------------------------

    def read_background_pha(self, bkgfile):
        """Open a pha file containing the background spectrum (if specified)."""
        if bkgfile is not None:
            stat = self.back.read(bkgfile)
            if stat != 0:
                print("Error: Unable to read background PHA file.")
                return
            else:
                self.input_back = True
        else:
            print("Error: No background filename specified.")

    # -----------------------------------------------------
    # Read an OGIP rmf file
    # -----------------------------------------------------

    def read_rmf(self, rmffile):
        """Open rmf file containing the response matrix."""
        stat = self.resp.read(rmffile)
        if stat != 0:
            print("Error: Unable to read RMF/RSP file.")
            return
        else:
            self.input_resp = True

    # -----------------------------------------------------
    # Read an OGIP arf file
    # -----------------------------------------------------

    def read_arf(self, arffile):
        """Read arf file containing the effective area."""
        if arffile is not None:
            stat = self.area.read(arffile)
            if stat != 0:
                print("Error: Unable to read ARF file.")
            self.input_area = True
            # Check if arf and rmf are compatible
            if self.resp.checkCompatibility(self.area) == 0:
                self.resp *= self.area
        else:
            print("Error: No effective area filename specified.")

    # -----------------------------------------------------
    # Read an OGIP corr file
    # -----------------------------------------------------

    def read_corr(self, corrfile):
        """Read correction file if specified."""
        if corrfile is not None:
            stat = self.corr.read(corrfile)
            if stat != 0:
                print("Error: Unable to read CORR file.")
            self.input_corr = True
        else:
            print("Error: No correction file specified.")

    # -----------------------------------------------------
    # Do a consistency check for the OGIP part
    # -----------------------------------------------------

    def check_ogip(self):
        """Check consistency of the OGIP files in this class."""

        # Check consistency of the source spectrum
        print("Check OGIP source spectrum... ", end='')
        spec = self.spec.check()
        if spec != '':
            print(spec)
            return 1
        else:
            print("OK")

        # Check consistency of the background spectrum
        if self.input_back:
            # Is the background file in order?
            print("Check OGIP background spectrum... ", end='')
            back = self.back.check()
            if back != '':
                print(back)
                return 1
            back = self.spec.checkCompatibility(self.back)
            if back != 0:
                print("Error: Background spectrum is not compatible with source spectrum.")
                return 1
            print("OK")

        # Check consistency of the correction spectrum
        if self.input_corr:
            # Is the correction file in order?
            print("Check OGIP correction spectrum... ", end='')
            corr = self.corr.check()
            if corr != '':
                print(corr)
                return 1
            corr = self.spec.checkCompatibility(self.corr)
            if corr != 0:
                print("Error: Correction spectrum is not compatible with source spectrum.")
                return 1
            print("OK")

        # Check rmf file
        print("Check OGIP response matrix... ", end='')
        resp = self.resp.check()
        if resp != '':
            print(resp)
            return 1
        print("OK")

        # Check consistency between ARF and RMF
        if self.input_area:
            # Is the effective area file in order?
            print("Check OGIP effective area file... ", end='')
            area = self.area.check()
            if area != '':
                print(area)
                return 1
            # Is the effective area consistent with the response?
            area = self.resp.checkCompatibility(self.area)
            if area != 0:
                print("Error: Effective area file is not consistent with the provided response file.")
                return 1
            print("OK")

        return 0

    # -----------------------------------------------------
    # Show a summary of the provided OGIP data
    # -----------------------------------------------------

    def show_ogip(self):
        """Shows a summary of the loaded OGIP data."""

        print("===========================================================")
        print("Summary of OGIP information:")
        print("===========================================================")

        print(self.spec.disp())

        if self.input_back:
            print(self.back.disp())
        else:
            print("No background spectrum provided.")
            print("")

        if self.input_corr:
            print(self.corr.disp())
        else:
            print("No correction spectrum provided.")
            print("")

        print(self.resp.disp())

        if self.input_area:
            print(self.area.disp())
        else:
            print("No effective area file provided.")
            print("")

        print("===========================================================")


    # -----------------------------------------------------
    # Return a spo object derived from the OGIP data
    # -----------------------------------------------------

    def ogip_to_spo(self):
        """Convert the source and optional background and correction spectra from OGIP to SPEX format. This
        method returns a pyspex Spo object containing the source and background rates. Please make sure that
        all necessary OGIP files are read in before running this method."""

        if not self.input_spec:
            print("Error: Spectrum has not been read in yet.")
            return

        spo = Spo()

        # Determine number of channels and add to spo
        nchan = self.spec.NumberChannels()
        spo.nchan = np.append(spo.nchan, nchan)
        spo.sponame = None

        # Initialize local arrays for spectral rates
        ochan = np.zeros(nchan, dtype=float)  # Local variable containing the source rate
        mbchan = np.zeros(nchan, dtype=float)  # Local variable containing the background rate
        dbchan = np.zeros(nchan, dtype=float)  # Local variable containing the error on the background
        corr = np.zeros(nchan, dtype=float)  # Local variable containing the correction spectrum

        # Read source rate per bin (or convert to rate)
        ochan = self.__read_counts_pha(self.spec, ochan, nchan)

        # Read background rate (or convert to rate) if available
        if self.input_back:
            mbchan = self.__read_counts_pha(self.back, mbchan, nchan)
            # If the error is provided in the file, use this column
            if hasattr(self.back, 'StatError') and not self.back.Poisserr:
                for i in np.arange(nchan):
                    if self.back.Datatype == "COUNT":
                        dbchan[i] = float(self.back.StatError[i]) / self.back.Exposure
                    elif self.back.Datatype == "RATE":
                        dbchan[i] = self.back.StatError[i]
                    else:
                        print("Error: Unknown datatype in source PHA file.")
                        return

            # If the error is not in the file, assume Poissonian errors
            else:
                for i in np.arange(nchan):
                    dbchan[i] = math.sqrt(mbchan[i] / self.back.Exposure)

        # Read correction spectrum if available
        if self.input_corr:
            corr = self.__read_counts_pha(self.corr, corr, nchan)

        # Create zero arrays of length nchan to fill in the loop later
        spo.zero_spo(nchan)

        # Loop through all the bins for the relevant spectral arrays
        for i in np.arange(nchan):
            spo.tints[i] = self.spec.Exposure * self.spec.AreaScaling[i]

            # Calculate the source rates and errors
            if spo.tints[i] > 0:
                spo.ochan[i] = ochan[i] / self.spec.AreaScaling[i]
                spo.dochan[i] = spo.ochan[i] / spo.tints[i]  # Add the errors in square later
            else:
                spo.ochan[i] = 0.
                spo.dochan[i] = 0.

            # Subtract background if available
            if self.input_back:
                btints = self.back.Exposure * self.back.AreaScaling[i]
                # Calculate backscale ratio
                if self.back.BackScaling[i] > 0:
                    fb = self.spec.BackScaling[i] / self.back.BackScaling[i]
                else:
                    fb = 0.

                # Subtract background and calculate errors
                spo.ochan[i] = spo.ochan[i] - mbchan[i] * fb / self.back.AreaScaling[i]
                spo.dochan[i] = spo.dochan[i] + (dbchan[i] * fb / self.back.AreaScaling[i]) ** 2
                spo.mbchan[i] = mbchan[i] * fb / self.back.AreaScaling[i]
                spo.dbchan[i] = (dbchan[i] * fb / self.back.AreaScaling[i]) ** 2

                # Calculate the Ext_Rate backscale ratio
                if fb > 0 and self.spec.Exposure > 0:
                    spo.brat[i] = btints / spo.tints[i] / fb
                else:
                    spo.brat[i] = 0.

            # Subtract correction spectrum, if available
            if self.input_corr:
                ctints = self.corr.Exposure * self.corr.AreaScaling[i]
                # Note: The influence of brat on the corr spectrum is not taken into account!
                if self.corr.BackScaling[i] > 0:
                    fc = self.spec.BackScaling[i] / self.corr.BackScaling[i]
                else:
                    fc = 0.

                # Subtract correction spectrum and calculate errors
                spo.ochan[i] = spo.ochan[i] - corr[i] * fc / ctints
                spo.dochan[i] = spo.dochan[i] + corr[i] * (fc / ctints) ** 2
                spo.mbchan[i] = spo.mbchan[i] + corr[i] * fc / ctints
                spo.dbchan[i] = spo.dbchan[i] + corr[i] * (fc / ctints) ** 2

            # Set background to zero for zero exposure bins
            if spo.tints[i] <= 0.:
                spo.mbchan[i] = 0.
                spo.dbchan[i] = 0.
                spo.brat[i] = 0.

            spo.dochan[i] = math.sqrt(spo.dochan[i])
            spo.dbchan[i] = math.sqrt(spo.dbchan[i])

            # Add systematic errors to spo file
            if self.spec.Datatype == "RATE":
                spo.ssys[i] = self.spec.SysError[i]
            else:
                if spo.tints[i] > 0:
                    spo.ssys[i] = self.spec.SysError[i] / spo.tints[i]
                else:
                    spo.ssys[i] = 0.

            if self.input_back:
                if self.back.Datatype == "RATE":
                    spo.bsys[i] = self.back.SysError[i]
                else:
                    spo.bsys[i] = self.back.SysError[i] / spo.tints[i]

            # Set first, last and used variables
            if self.spec.Quality[i] != 0:
                spo.used[i] = False

            if self.input_back:
                if self.back.Quality[i] != 0:
                    spo.used[i] = False

            if self.input_corr:
                if self.corr.Quality[i] != 0:
                    spo.used[i] = False

            if self.save_grouping:
                if self.spec.Grouping[i] == 1:
                    spo.first[i] = True
                    spo.last[i] = False
                if self.spec.Grouping[i] == 0:
                    spo.first[i] = False
                    if i < nchan - 1:
                        if self.spec.Grouping[i + 1] == 1:
                            spo.last[i] = True
                    elif i == nchan - 1:
                        spo.last[i] = True
                    else:
                        spo.last[i] = False

            # Get channel boundaries from response
            # Channel boundary cannot be 0.
            if self.resp.EnergyUnits != "keV":
                print("Warning: Energy units of keV are expected in the response file!")

            if self.resp.ChannelLowEnergy[i] <= 0.:
                spo.echan1[i] = 1e-5
                print("Warning: Lowest channel boundary energy is 0. Set to 1E-5 to avoid problems.")
            else:
                spo.echan1[i] = self.resp.ChannelLowEnergy[i]
            spo.echan2[i] = self.resp.ChannelHighEnergy[i]

        # Check if channel order needs to be swapped
        if nchan > 1:
            if spo.echan1[0] > spo.echan1[1]:
                spo.swap = True
                spo.swap_order()

        spo.empty=False

        return spo

    # Helper function for ogip_to_spo
    def __read_counts_pha(self, input_pha, outarray, nchan):
        for i in np.arange(nchan):
            if input_pha.Datatype == "COUNT":
                outarray[i] = float(input_pha.Pha[i]) / input_pha.Exposure
            elif input_pha.Datatype == "RATE":
                outarray[i] = input_pha.Pha[i]
            else:
                print("Error: Unknown datatype in source PHA file.")
                return

        return outarray

    # -----------------------------------------------------
    # Return a res object derived from the OGIP data
    # -----------------------------------------------------

    def ogip_to_res(self):
        """Convert response matrix from OGIP to SPEX format. The response matrix is translated one-to-one
        without optimizations. All groups in the OGIP matrix are put into one SPEX response component. This
        method returns a pyspex Res object containing the response matrix."""

        try:
            self.resp.NumberChannels()
        except NameError:
            print("Error: The OGIP response matrix has not been initialised yet.")
            return 0

        if not self.input_resp:
            print("Error: The OGIP response matrix has not been read yet.")
            return 0

        res = Res()

        # Read the number of energy bins and groups
        res.nchan = np.append(res.nchan, self.resp.NumberChannels())
        res.nsector = 1
        res.nregion = 1
        res.sector = np.append(res.sector, 1)
        res.region = np.append(res.region, 1)
        res.resname = None

        # Read the total number of groups (which is neg in SPEX format)
        res.neg = np.append(res.neg, self.resp.NumberTotalGroups())

        res.eg1 = np.zeros(res.neg, dtype=float)
        res.eg2 = np.zeros(res.neg, dtype=float)
        res.nc = np.zeros(res.neg, dtype=int)
        res.ic1 = np.zeros(res.neg, dtype=int)
        res.ic2 = np.zeros(res.neg, dtype=int)

        # Read the total number of matrix elements
        nm = self.resp.NumberTotalElements()
        res.resp = np.zeros(nm, dtype=float)

        # Set the number of components to 1 (no optimization or re-ordering)
        res.ncomp = 1

        # Read the energy bin boundaries and group information
        g = 0  # Index for the group number
        m = 0  # Index for the matrix element number
        for i in np.arange(self.resp.NumberEnergyBins()):
            # Number of response groups for this energy bin
            ngrp = self.resp.NumberGroups[i]
            for j in np.arange(ngrp):
                # Energy bin boundaries
                if self.resp.LowEnergy[i] <= 0.:
                    res.eg1[g] = 1e-7
                    print("Warning: Lowest energy boundary is 0. Set to 1E-7 to avoid problems.")
                else:
                    res.eg1[g] = self.resp.LowEnergy[i]

                res.eg2[g] = self.resp.HighEnergy[i]
                if res.eg2[g] <= res.eg1[g]:
                    print("Error: Discontinous bins in energy array in channel {0}. Please check the numbers.".format(
                        i + 1))
                    return

                res.nc[g] = self.resp.NumberChannelsGroup[g]
                res.ic1[g] = self.resp.FirstChannelGroup[
                                 g] + 1  # +1 because C++ starts counting at 0 and Fortran with 1
                ic2 = res.ic1[g] + res.nc[g] - 1
                res.ic2[g] = ic2

                for k in np.arange(res.nc[g]):
                    res.resp[m] = self.resp.Matrix[m]
                    m = m + 1
                g = g + 1

        if g > res.neg:
            print("Error: Mismatch between number of groups.")
            return 0

        if m > nm:
            print("Error: Mismatch between number of matrix elements.")
            return 0

        # Convert matrix to m**2 units for SPEX
        if self.input_area:
            if self.area.arfUnits == "cm2":
                res.resp *= 1.E-4

        # Check if channel order needs to be swapped
        if res.nchan > 1:
            if self.resp.ChannelLowEnergy[0] > self.resp.ChannelLowEnergy[1]:
                res.swap = True
                res.swap_order()

        res.empty = False

        return res
