#!/usr/bin/env python

import math
import pyspextools.messages as message


def gaussrsp(x, mu, fwhm, dfwhm):
    """Gaussian response function, optionally as a linear function of energy. The inputs are the energy value to
    calculate the response for (x), the center of the Gauss function (mu), the resolution of the detector
    (FWHM in eV at 1 keV), and the gradient of the FWHM as a function of energy.

    :param x: X value to calculate response for.
    :type x: float
    :param mu: Center of the Gauss function.
    :type mu: float
    :param fwhm: The full-width at half maximum of the detector resolution (FWHM in eV at 1 keV).
    :type fwhm: float
    :param dfwhm: Gradient of the detector resolution as a function of energy.
    :type dfwhm: float
    """

    # FWHM at the center energy of the response
    fwhm_mu = fwhm + dfwhm * (mu - 1.0)
    if fwhm_mu <= 0.:
        message.error('The FWHM has become (less than) 0 in the provided energy range. '
                      'Please check your input gradient.')
        return -1

    # Convert the FWHM to sigma
    sigma = fwhm_mu / (2.0 * math.sqrt(2.0*math.log(2.0)))

    # Convert sigma to keV
    sigma = sigma * 1E-3

    # Calculate the response value for this response element x
    resp = 1./(sigma * math.sqrt(2.*math.pi)) * math.exp(-(x-mu)**2/(2. * sigma**2))

    return resp