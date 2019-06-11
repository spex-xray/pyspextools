#!/usr/bin/env python

# Import stuff for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import pyspextools.messages as message
import numpy as np
import math
import os


from .region import Region
from .res import Res
from .spo import Spo
from .pha import Pha
from .rmf import Rmf
from .arf import Arf

standard_library.install_aliases()

# -----------------------------------------------------
# Return a spo object derived from the OGIP data
# -----------------------------------------------------

def pha_to_spo(src,rmf,back=None,corr=None,save_grouping=False):
    """Convert the source (src) and optional background (back) and correction spectra (corr) from OGIP to SPEX format. 
    Please also provide an OGIP rmf object from the Rmf class to this function to read the channel energies.
    When the save_grouping flag is true, the grouping information in the PHA file will be copied to the spo file.
    The default behaviour is to ignore the grouping.
    This method returns a pyspextools Spo object containing the source and background rates."""

    if not isinstance(src, Pha):
        message.error("Input source spectrum is not a PHA object.")
        return 1
    
    if not isinstance(rmf, Rmf):
        message.error("Input response matrix is not an RMF object.")
        return 1
    
    if back is not None:
        if not isinstance(back, Pha):
            message.error("Input background spectrum is not a PHA object.")
            return 1
        input_back = True
    else:
        input_back = False
        
    if corr is not None:
        if not isinstance(corr, Pha):
            message.error("Input correction spectrum is not a PHA object.")
            return 1
        input_corr = True
    else:
        input_corr = False

    spo = Spo()

    # Determine number of channels and add to spo
    spo.nchan = np.append(spo.nchan, src.DetChans)
    spo.sponame = None
    spo.nregion = 1

    # Create zero arrays of length nchan to fill in the loop later
    spo.zero_spo(src.DetChans)

    # Loop through all the bins for the relevant spectral arrays
    for i in np.arange(src.DetChans):
        spo.tints[i] = src.Exposure * src.AreaScaling[i]

        # Calculate the source rates and errors
        if spo.tints[i] > 0:
            spo.ochan[i] = src.Rate[i] / src.AreaScaling[i]
            spo.dochan[i] = (src.StatError[i])**2 / src.AreaScaling[i]  # Add the errors in square later
        else:
            spo.ochan[i] = 0.
            spo.dochan[i] = 0.

        # Subtract background if available
        if input_back:
            btints = back.Exposure * back.AreaScaling[i]
            # Calculate backscale ratio
            if back.BackScaling[i] > 0:
                fb = src.BackScaling[i] / back.BackScaling[i]
            else:
                fb = 0.

            # Subtract background and calculate errors
            spo.ochan[i] = spo.ochan[i] - back.Rate[i] * fb / back.AreaScaling[i]
            spo.dochan[i] = spo.dochan[i] + (back.StatError[i] * fb / back.AreaScaling[i]) ** 2
            spo.mbchan[i] = back.Rate[i] * fb / back.AreaScaling[i]
            spo.dbchan[i] = (back.StatError[i] * fb / back.AreaScaling[i]) ** 2

            # Calculate the Exp_Rate backscale ratio
            if fb > 0 and src.Exposure > 0:
                spo.brat[i] = btints / spo.tints[i] / fb
            else:
                spo.brat[i] = 0.

        # Subtract correction spectrum, if available
        if input_corr:
            ctints = corr.Exposure * corr.AreaScaling[i]
            # Note: The influence of brat on the corr spectrum is not taken into account!
            if corr.BackScaling[i] > 0:
                fc = src.BackScaling[i] / corr.BackScaling[i]
            else:
                fc = 0.

            # Subtract correction spectrum and calculate errors
            spo.ochan[i] = spo.ochan[i] - corr.Rate[i] * fc / ctints
            spo.dochan[i] = spo.dochan[i] + corr.Rate[i] * (fc / ctints) ** 2
            spo.mbchan[i] = spo.mbchan[i] + corr.Rate[i] * fc / ctints
            spo.dbchan[i] = spo.dbchan[i] + corr.Rate[i] * (fc / ctints) ** 2

        # Set background to zero for zero exposure bins
        if spo.tints[i] <= 0.:
            spo.mbchan[i] = 0.
            spo.dbchan[i] = 0.
            spo.brat[i] = 0.

        spo.dochan[i] = math.sqrt(spo.dochan[i])
        spo.dbchan[i] = math.sqrt(spo.dbchan[i])

        # Set first, last and used variables
        if src.Quality[i] != 0:
            spo.used[i] = False

        if input_back:
            if back.Quality[i] != 0:
                spo.used[i] = False

        if input_corr:
            if corr.Quality[i] != 0:
                spo.used[i] = False

        if save_grouping:
            if src.Grouping[i] == 1:
                spo.first[i] = True
                spo.last[i] = False
            if src.Grouping[i] == 0:
                spo.first[i] = False
                if i < src.DetChans - 1:
                    if src.Grouping[i + 1] == 1:
                        spo.last[i] = True
                elif i == src.DetChans - 1:
                    spo.last[i] = True
                else:
                    spo.last[i] = False

        # Get channel boundaries from response
        # Channel boundary cannot be 0.
        if rmf.EnergyUnits != "keV":
            message.warning("Energy units of keV are expected in the response file!")

        if rmf.ChannelLowEnergy[i] <= 0.:
            spo.echan1[i] = 1e-5
            message.warning("Lowest channel boundary energy is 0. Set to 1E-5 to avoid problems.")
        else:
            spo.echan1[i] = rmf.ChannelLowEnergy[i]
        spo.echan2[i] = rmf.ChannelHighEnergy[i]

    # Check if channel order needs to be swapped
    if src.DetChans > 1:
        if spo.echan1[0] > spo.echan1[1]:
            spo.swap = True
            spo.swap_order()

    spo.empty=False

    return spo

# -----------------------------------------------------
# Return a res object derived from the OGIP data
# -----------------------------------------------------

def rmf_to_res(rmf, arf=None):
    """Convert an response matrix object from OGIP to SPEX format. The response matrix is translated one-to-one
    without optimizations. Providing an ARF object is optional. All groups in the OGIP matrix are put into one
    SPEX response component. This method returns a pyspextools Res object containing the response matrix."""

    if not isinstance(rmf, Rmf):
        message.error("The input RMF object is not of type Rmf.")
        return 1

    if arf is not None:
        if not isinstance(arf, Arf):
            message.error("The input ARF object is not of type Arf.")
        input_area = True
    else:
        input_area = False

    try:
        rmf.NumberChannels
    except NameError:
        message.error("The OGIP response matrix has not been initialised yet.")
        return 0

    res = Res()

    # Read the number of energy bins and groups
    res.nchan = np.append(res.nchan, rmf.NumberChannels)
    res.nsector = 1
    res.nregion = 1
    res.sector = np.append(res.sector, 1)
    res.region = np.append(res.region, 1)
    res.resname = None

    # Read the total number of groups (which is neg in SPEX format)
    res.neg = np.append(res.neg, rmf.NumberTotalGroups)

    res.eg1 = np.zeros(res.neg, dtype=float)
    res.eg2 = np.zeros(res.neg, dtype=float)
    res.nc = np.zeros(res.neg, dtype=int)
    res.ic1 = np.zeros(res.neg, dtype=int)
    res.ic2 = np.zeros(res.neg, dtype=int)

    # Read the total number of matrix elements
    nm = rmf.NumberTotalElements
    res.resp = np.zeros(nm, dtype=float)

    # Set the number of components to 1 (no optimization or re-ordering)
    res.ncomp = 1

    # Read the energy bin boundaries and group information
    g = 0  # Index for the group number
    m = 0  # Index for the matrix element number
    for i in np.arange(rmf.NumberEnergyBins):
        # Number of response groups for this energy bin
        ngrp = rmf.NumberGroups[i]
        for j in np.arange(ngrp):
            # Energy bin boundaries
            if rmf.LowEnergy[i] <= 0.:
                res.eg1[g] = 1e-7
                message.warning("Lowest energy boundary is 0. Set to 1E-7 to avoid problems.")
            else:
                res.eg1[g] = rmf.LowEnergy[i]

            res.eg2[g] = rmf.HighEnergy[i]
            if res.eg2[g] <= res.eg1[g]:
                message.error("Discontinous bins in energy array in channel {0}. Please check the numbers.".format(
                    i + 1))
                return

            res.nc[g] = rmf.NumberChannelsGroup[g]
            # Add the start channel to the IC to correct for cases where we start at channel 0/1
            res.ic1[g] = rmf.FirstChannelGroup[g]
            ic2 = res.ic1[g] + res.nc[g] - 1
            res.ic2[g] = ic2

            if input_area:
                area=arf.EffArea[i]
            else:
                area = 1.0

            for k in np.arange(res.nc[g]):
                res.resp[m] = rmf.Matrix[m] * area
                if res.resp[m] < 0.0:
                    res.resp[m] = 0.0
                m = m + 1
            g = g + 1

    if g > res.neg:
        message.error("Mismatch between number of groups.")
        return 0

    if m > nm:
        message.error("Mismatch between number of matrix elements.")
        return 0

    # Convert matrix to m**2 units for SPEX
    if input_area:
        if arf.ARFUnits == "cm2":
            res.resp *= 1.E-4
    else:
        res.resp *= 1.E-4

    # Check if channel order needs to be swapped
    if res.nchan > 1:
        if rmf.ChannelLowEnergy[0] > rmf.ChannelLowEnergy[1]:
            res.swap = True
            res.swap_order()

    res.empty = False

    return res

