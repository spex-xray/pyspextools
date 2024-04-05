#!/usr/bin/env python

# =========================================================
"""
  Python module to organise SPEX res and spo files into regions.
  See this page for the format specification:

    https://spex-xray.github.io/spex-help/theory/response.html

  This module contains the Region class:

    Region:    Contains the the combination of a spectrum and a
               response organized in a SPEX region

  Dependencies:
    - numpy:      Array operations
    - spo:        The spo class from this pyspextools data module
    - res:        The res class from this pyspextools data module
"""
# =========================================================

import numpy as np

from pyspextools.io.spo import Spo
from pyspextools.io.res import Res
import pyspextools.messages as message


# =========================================================
# Region class
# =========================================================

class Region:
    """A SPEX region is a spectrum/response combination for a
    specific observation, instrument or region on the sky.
    It combines the spectrum and response file in one object.

    :ivar spo: Spo object
    :vartype spo: pyspextools.io.Spo
    :ivar res: Res object
    :vartype res: pyspextools.io.Res
    """

    def __init__(self):
        self.spo = Spo()        # Spo object
        self.res = Res()        # Res object
        self.label = ""         # Optional region label (will not be written to file). For example: MOS1, annulus2, etc.

        # Arrays for optimal binning
        self.response = np.array([], dtype=float)    #
        self.nrcomp = np.array([], dtype=int)       # Number of response components


    def change_label(self, label):
        """Attach a label to this region to easily identify it. For example: MOS1, annulus 2, etc.

        :param label: Text string to identify region.
        :type label: str
        """
        self.label = str(label)

    def set_sector(self, sector):
        """Set the sector number for this region.

        :param sector: Sector number to set for this region.
        :type sector: int
        """

        for i in np.arange(self.res.sector.size):
            self.res.sector[i] = sector

    def set_region(self, region):
        """Set the region number for this region.

        :param region: Region number to set for this region.
        :type region: int
        """

        for i in np.arange(self.res.region.size):
            self.res.region[i] = region

    def increase_region(self, amount):
        """Increase the region numbers by an integer amount.

        :param amount: Integer amount to add to region numbers.
        :type amount: int
        """

        for i in np.arange(self.res.region.size):
            self.res.region[i] = self.res.region[i] + amount

    def fwhm(self):
        """Determine the spectral resolution (FWHM) for each response element."""

        if self.res.init_fwhm:
            return
        else:
            self.res.initialize_fwhm()

        self.nrcomp = np.zeros(self.res.ncomp, dtype=int)

        # Loop over the response components in the res object
        for i in np.arange(self.res.ncomp):
            # Determine the region number for this component and find the related spectrum
            ireg = self.res.region[i]
            self.response = np.zeros(self.spo.nchan[ireg])
            sporeg = self.spo.return_region(ireg)

            # Loop over energies in component
            ie1 = 0

            while ie1 < self.res.neg[i]:
                g1 = self.res.get_response_group(i, ie1)
                if g1.nc == 0:
                    continue

                # Check if bins have the same energy and need to be combined
                ie2 = ie1
                while True:
                    ie2 += 1
                    g2 = self.res.get_response_group(i, ie2)
                    if g2.nc == 0:
                        continue
                    if g2.eg1 > g1.eg1:
                        break

                ie2 = min(ie2 - 1, self.res.neg[i])

                # Make response column for the present energy
                ic1 = g1.ic1
                ic2 = ic1
                for ie in range(ie1, ie2):
                    ge = self.res.get_response_group(i, ie)
                    if ge.nc == 0:
                        continue
                    self.response[ge.ic1:ge.ic2+1] = self.response[ge.ic1:ge.ic2+1] + ge.resp
                    ic1 = min(ic1, ge.ic1)
                    ic2 = max(ic2, ge.ic2)

                nc = ic2 - ic1 + 1

                # Determine the values ec1 and ec2 at half maximum, as well as centroid ec

                # Start fwhm_resp

                # Determine the nearest point to the maximum
                imax = int(np.argmax(self.response))

                # Interpolate the actual maximum value using quadratic fitting
                i1 = int(max(imax-1, 0))              # Maximum point -1, but at least 0
                i2 = int(min(i1+2, nc - 1))           # Minimum point + 2, but prevent overflow
                npol = i2 - i1 + 1

                if npol <= 2:
                    xc = float(imax)
                    resp_max = self.response[imax]
                else:
                    delta = self.response[i1] + self.response[i2] - 2.0 * self.response[i1+1]
                    if delta >= 0:
                        xc = float(imax)
                        resp_max = self.response[imax]
                    else:
                        xc = (self.response[i1] - self.response[i2]) / (2.0 * delta)
                        resp_max = self.response[i1+1] - 0.5 * delta * xc**2
                        xc = xc + float(i1 + 1)
                        if (xc > float(i2)) or (xc < float(i1)):
                            xc = float(imax)
                            resp_max = self.response[imax]

                # Shortcut for zero effective area cases
                if resp_max <= 0.0:
                    ec = sporeg.echan1[imax]
                    ec1 = ec
                    ec2 = ec
                    return

                # Next determine half maximum
                half_max = resp_max / 2.0
                ic = int(np.rint(xc))
                i1 = ic
                while i1 > 0:
                    if self.response[i1] < half_max:
                        break
                    i1 = i1 - 1

                # See if we get a good point and do linear interpolation


                # !!! Check the counting carefully! No offsets ???


                if self.response[i1] < half_max:
                    x1 = float(i1) + (half_max - self.response[i1]) / (self.response[i1+1] - self.response[i1])
                else:
                    x1 = 1.0

                i2 = ic
                while i2 < nc:
                    if self.response[i2] < half_max:
                        break
                    i2 = i2 + 1

                if self.response[i2] < half_max:
                    x2 = float(i2) + (half_max - self.response[i2]) / (self.response[i2] - self.response[i2-1])
                else:
                    x2 = float(nc)

                # Add offsets
                x1 = x1 + (ic1 - 1)
                x2 = x2 + (ic1 - 1)
                xc = xc + (ic1 - 1)

                ic = int(np.rint(xc))
                ec = sporeg.echan1[ic] + (float(xc) - float(ic) + 0.5) * (sporeg.echan2[ic] - sporeg.echan1[ic])
                ic = int(np.rint(x1))
                ec1 = sporeg.echan1[ic] + (x1 - ic + 0.5) * (sporeg.echan2[ic] - sporeg.echan1[ic])
                ic = int(np.rint(x2))
                ec2 = sporeg.echan1[ic] + (x2 - ic + 0.5) * (sporeg.echan2[ic] - sporeg.echan1[ic])

                # End fwhm_resp

                for ie in range(ie1, ie2):
                    ge = self.res.get_response_group(i, ie)
                    fwhm = ec2 - ec1
                    if fwhm > 0:
                        self.res.r = self.res.r + (ge.eg2 - ge.eg1) / fwhm

                #
                # Determine the number of counts within the resolution element
                #

                # Begin of fwhm_n

                # Determine array cumobs: cumulative number of counts up to and including the current data channel
                # Determine array cumres: cumulative response up to and including the current data channel
                # Determine array echan: Channel boundaries

                n = sporeg.nchan + 1

                echan = np.zeros(n, dtype=float)
                cumobs = np.zeros(n, dtype=float)
                cumres = np.zeros(n, dtype=float)

                echan[:n-2] = sporeg.echan1
                echan[n-1] = sporeg.echan2[n-1]

                cum = 0.0
                res = 0.0

                iresp = self.response[ic1:ic2]

                j = 1 - ic1
                for k in np.arange(sporeg.nchan):
                    cumobs[k] = cum
                    cum = cum + sporeg.tints[k] * sporeg.ochan[k]
                    j = j + 1
                    if (j > 0) and (j <= nc):
                        cumres[k] = res
                        res = res + iresp[j]

                cumobs[n] = cum
                cumres[n] = res
                if res > 0.0:
                    cumres = cumres / res

                # Interpolate both for ec1 and ec2
                for k in np.arange(2):
                    if k == 0:
                        ec = ec1
                    else:
                        ec = ec2

                    ilk = np.searchsorted(echan, ec)
                    if ilk == 0.0:
                        cum = 0.0
                        rsc = 0.0
                    elif ilk == n:
                        cum = cumobs[n]
                        rsc = cumres[n]
                    else:
                        cum = np.interp(ec, echan, cumobs)
                        rsc = np.interp(ec, echan, cumres)

                    if k == 0:
                        cum1 = cum
                        res1 = rsc
                    else:
                        cum2 = cum
                        res2 = rsc

                rcount = max(0.0, cum2-cum1)    # Make sure rcount is non-negative
                r = max(0.0, res2-res1)         # Make sure r is non-negative

                if r > 0.0:
                    rcount = rcount / r    # Correct for finite number of counts within FWHM

                if res == 0.0:
                    rcount = 0.0           # solution for pathological cases where response is 0

                rcount = max(rcount, 1.0)  # Make rcount at least 1 to prevent crashes

                # End of fwhm_n

                for ie in range(ie1, ie2):
                    ge = self.res.get_response_group(i, ie)
                    self.res.rcount[ge.i] = rcount

                # End of while loop
                ie1 = ie2 + 1

            self.res.r = max(1, self.res.r)
            return

    def obin(self):
        """Optimally bin the spectrum and the response."""

        # First phase: determine effective resolution for data and model
        self.fwhm()





    def check(self, nregion=False):
        """Check whether spectrum and response are compatible
        and whether the arrays really consist of one region (if nregion flag is set).

        :param nregion: Flag to check whether the arrays just contain one region.
        :type nregion: bool
        """

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

    def show(self, isector=1, iregion=1):
        """Show a summary of the region metadata.

        :param isector: Sector number to show.
        :type isector: int
        :param iregion: Region number to show.
        :type iregion: int
        """

        print("===========================================================")
        print(" Sector:            {0}  =>  Region:            {1}".format(str(self.res.sector[0]),
              str(self.res.region[0])))
        print(" Label:             {0}".format(self.label))

        print(" --------------------  Spectrum  -------------------------")
        self.spo.show()

        print(" --------------------  Response  -------------------------")
        self.res.show(isector=isector, iregion=iregion)
