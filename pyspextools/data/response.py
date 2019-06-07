#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyspextools.messages as message

import math

# Stuff to import for compatibility between python 2 and 3
from builtins import int

from future import standard_library

standard_library.install_aliases()

def gaussrsp(x, mu, fwhm, dfwhm):
    '''Gaussian response function, optionally as a linear function of energy. The inputs are the energy value to
    calculate the response for (x), the center of the Gauss function (mu), the resolution of the detector
    (FWHM in eV at 1 keV), and the gradient of the FWHM as a function of energy.'''

    # FWHM at the center energy of the response
    fwhm_mu = fwhm + dfwhm * (mu - 1.0)

    # Convert the FWHM to sigma
    sigma = fwhm_mu / (2.0 * math.sqrt(2.0*math.log(2.0)))

    # Convert sigma to keV
    sigma = sigma * 1E-3

    # Calculate the response value for this response element x
    resp = 1./(sigma * math.sqrt(2.*math.pi)) * math.exp(-(x-mu)**2/(2. * sigma**2))

    return resp