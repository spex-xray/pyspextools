#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyspextools.io.region import Region
import pyspextools.messages as message

import numpy as np

# Stuff to import for compatibility between python 2 and 3
from builtins import int

from future import standard_library

standard_library.install_aliases()


def clean_region(reg):
    """Remove bad channels and channels with zero response from the region."""

    if not isinstance(reg, Region):
        message.error("The input object is not of type Region.")
        return 1

    if reg.spo.empty:
        message.error("The input spo object is empty.")
        return -1

    if reg.res.empty:
        message.error("The input spo object is empty.")
        return -1

    message.proc_start("Identify bad channels in spectrum and response matrix and re-index matrix")

    (chanmask, groupmask, respmask) = __get_bad_channel_masks(reg)

    message.proc_end(0)

    # Print number of good and bad channels
    goodchan = np.sum(chanmask)
    badchan = chanmask.size - goodchan

    print("Number of good channels: {0}".format(goodchan))
    print("Number of bad channels:  {0}".format(badchan))

    message.proc_start("Removing bad channels from spectral region")

    spo = reg.spo

    spo.echan1 = reg.spo.echan1[chanmask]
    spo.echan2 = reg.spo.echan2[chanmask]
    spo.tints = reg.spo.tints[chanmask]
    spo.ochan = reg.spo.ochan[chanmask]
    spo.dochan = reg.spo.dochan[chanmask]
    spo.mbchan = reg.spo.mbchan[chanmask]
    spo.dbchan = reg.spo.dbchan[chanmask]
    spo.brat = reg.spo.brat[chanmask]
    spo.ssys = reg.spo.ssys[chanmask]
    spo.bsys = reg.spo.bsys[chanmask]
    spo.used = reg.spo.used[chanmask]
    spo.first = reg.spo.first[chanmask]
    spo.last = reg.spo.last[chanmask]

    # Count the number of good channels
    for i in np.arange(spo.nregion):
        spo.nchan[i] = np.sum(chanmask)

    # Check the consistency of the new object
    stat = spo.check()

    # Show result to user
    message.proc_end(stat)

    # Copy the filtered object to the original region
    reg.spo = spo

    # Print number of good and bad groups
    badgroup = groupmask.size - np.sum(groupmask)

    print("Number of original groups:       {0}".format(groupmask.size))
    print("Number of zero-response groups:  {0}".format(badgroup))

    # Print number of removed response elements
    badelements = respmask.size - np.sum(respmask)

    print("Number of original response elements:  {0}".format(respmask.size))
    print("Number of bad response elements:       {0}".format(badelements))

    message.proc_start("Removing bad channels from response matrix")

    # Mask response array
    reg.res.resp = reg.res.resp[respmask]
    if reg.res.resp_der:
        reg.res.dresp = reg.res.dresp[respmask]

    # Mask group arrays
    reg.res.eg1 = reg.res.eg1[groupmask]
    reg.res.eg2 = reg.res.eg2[groupmask]
    reg.res.ic1 = reg.res.ic1[groupmask]
    reg.res.ic2 = reg.res.ic2[groupmask]
    reg.res.nc = reg.res.nc[groupmask]
    if reg.res.area_scal:
        reg.res.relarea = reg.res.relarea[groupmask]

    eg_start = 0

    for icomp in np.arange(reg.res.ncomp):
        reg.res.nchan[icomp] = np.sum(chanmask)
        eg_end = reg.res.neg[icomp] + eg_start
        reg.res.neg[icomp] = np.sum(groupmask[eg_start:eg_end])
        eg_start = eg_end + 1

    stat = reg.res.check()

    message.proc_end(stat)

    return reg


def __get_bad_channel_masks(reg):
    """Identify channels with zero response."""

    # Get the amount of channels and create a channel chanmask with that size
    chanmask = np.zeros(reg.spo.used.size, dtype=bool)

    if reg.spo.nchan != reg.spo.used.size:
        message.error("Mismatch in number of channels in spo object.")
        return 1

    if chanmask.size != reg.res.nchan[0]:
        message.error("Mismatch in number of channels between res and spo object.")
        return 1

    # Create a mask array for the number of groups (all true)
    groupmask = np.ones(reg.res.nc.size, dtype=bool)

    if groupmask.size != np.sum(reg.res.neg):
        message.error("Mismatch between the number of groups in the ICOMP and GROUP extensions.")
        return 1

    # Create a mask array for the number of response elements (all true)
    respmask = np.ones(reg.res.resp.size, dtype=bool)

    if respmask.size != np.sum(reg.res.nc):
        message.error("Mismatch between the number of response elements in the GROUP and RESP extensions.")
        return 1

    ir = 0
    # Loop over groups to find zero response elements and finalize channel mask
    for ie in np.arange(reg.res.eg1.size):
        ic1 = reg.res.ic1[ie]  # Original first channel of group
        ic2 = reg.res.ic2[ie]  # Original last channel of group
        for j in np.arange(reg.res.nc[ie]):
            ic = ic1 + j - 1  # -1 because Python array starts at 0, not 1
            if ic > ic2 - 1:
                message.error("Error: Mismatch in number of channels.")
            if reg.res.resp[ir] <= 0.0:
                chanmask[ic] = False or chanmask[ic]
            else:
                chanmask[ic] = True

            ir = ir + 1

    chanmask = np.logical_and(chanmask, reg.spo.used)

    # Loop over groups to set the new channel boundaries and fill respmask
    newie = 0  # Index of energy bins
    ir = 0  # Index of response elements in original array (at maximum reg.res.resp.size)

    for ie in np.arange(reg.res.eg1.size):

        ic1 = reg.res.ic1[ie]  # Original first channel of group
        first = True  # Is this the first channel of the group?
        newnc = 0

        for j in np.arange(reg.res.nc[ie]):
            ic = ic1 + j - 1
            if chanmask[ic]:  # If channel is good
                newnc = newnc + 1  # Count number of good channels in group
                if first:  # If this is the first good bin of the group, set ic1
                    first = False
                    reg.res.ic1[ie] = np.sum(chanmask[0:ic]) + 1
            else:
                respmask[ir] = False

            ir = ir + 1

        # Set new ic1, ic2 and nc
        reg.res.ic2[ie] = reg.res.ic1[ie] + newnc - 1
        reg.res.nc[ie] = reg.res.ic2[ie] - reg.res.ic1[ie] + 1

        if newnc == 0:
            groupmask[ie] = False
        else:
            newie = newie + 1

    return chanmask, groupmask, respmask
