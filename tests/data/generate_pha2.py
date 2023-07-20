#!/usr/bin/env python

from astropy.io import fits
import numpy as np

def main():
    # Create PHA2 file.
    c1 = fits.Column(name='SPEC_NUM', array=np.array([1, 2]), format='I')
    c2 = fits.Column(name='TG_M', array=np.array([-1, 1]), format='I')
    c3 = fits.Column(name='TG_PART', array=np.array([3, 3]), format='I')
    c4 = fits.Column(name='TG_SRCID', array=np.array([1, 1]), format='I')
    c5 = fits.Column(name='X', array=np.array([0.0, 0.0]), format='E')
    c6 = fits.Column(name='Y', array=np.array([0.0, 0.0]), format='E')
    c7 = fits.Column(name='CHANNEL', array=np.array([[1, 2, 3], [1, 2, 3]]), format='3I')
    c8 = fits.Column(name='COUNTS', array=np.array([[4, 4, 4], [4, 4, 4]]), format='3I')
    c9 = fits.Column(name='STAT_ERR', array=np.array([[2., 2., 2.], [2., 2., 2.]]), format='3E')
    c10 = fits.Column(name='BACKGROUND_UP', array=np.array([[0, 0, 0], [0, 0, 0]]), format='3I')
    c11 = fits.Column(name='BACKGROUND_DOWN', array=np.array([[0, 0, 0], [0, 0, 0]]), format='3I')
    c12 = fits.Column(name='BIN_LO', array=np.array([[1., 2., 3.], [1., 2., 3.]]), format='3D')
    c13 = fits.Column(name='BIN_HI', array=np.array([[2., 3., 4.], [2., 3., 4.]]), format='3D')

    pha2 = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13])
    pha2.header.set('EXTNAME', 'SPECTRUM')
    pha2.header.set('TELESCOP', 'CHANDRA', '')
    pha2.header.set('INSTRUME', 'HRC', '')
    pha2.header.set('GRATING', 'LETG')
    pha2.header.set('EXPOSURE', 1000.0)
    pha2.header.set('CORRSCAL', 0.0)
    pha2.header.set('BACKSCAL', 1.0)
    pha2.header.set('AREASCAL', 1.0)
    pha2.header.set('BACKSCUP', 1.0)
    pha2.header.set('BACKSCDN', 1.0)
    pha2.header.set('HDUCLAS2', 'SRC')
    pha2.header.set('HDUCLAS3', 'COUNTS')

    pha2.writeto("pha2.fits", overwrite=True)

    # Create ARF file
    c1 = fits.Column(name='ENERG_LO', array=np.array([1., 2., 3.]), format='E', unit='keV')
    c2 = fits.Column(name='ENERG_HI', array=np.array([2., 3., 4.]), format='E', unit='keV')
    c3 = fits.Column(name='SPECRESP', array=np.array([1., 1., 1.]), format='E', unit='cm**2')
    c4 = fits.Column(name='BIN_LO', array=np.array([1., 2., 3.]), format='E')
    c5 = fits.Column(name='BIN_HI', array=np.array([2., 3., 4.]), format='E')
    c6 = fits.Column(name='FRACEXPO', array=np.array([0., 0., 0.]), format='E')
    c7 = fits.Column(name='PHAFRAC', array=np.array([1., 1., 1.]), format='E')

    arf2 = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6, c7])
    arf2.header.set('EXTNAME', 'SPECRESP')
    arf2.writeto("arf2_-1.fits", overwrite=True)
    arf2.writeto("arf2_1.fits", overwrite=True)

    # Create RMF file
    ## EBOUNDS
    c1 = fits.Column(name='CHANNEL', array=np.array([1, 2, 3]), format='I')
    c2 = fits.Column(name='E_MIN', array=np.array([1., 2., 3.]), format='E', unit='keV')
    c3 = fits.Column(name='E_MAX', array=np.array([2., 3., 4.]), format='E', unit='keV')

    ebounds = fits.BinTableHDU.from_columns([c1, c2, c3])
    ebounds.header.set('EXTNAME', 'EBOUNDS')

    ## MATRIX
    c1 = fits.Column(name='ENERG_LO', array=np.array([1., 2., 3.]), format='E', unit='keV')
    c2 = fits.Column(name='ENERG_HI', array=np.array([2., 3., 4.]), format='E', unit='keV')
    c3 = fits.Column(name='N_GRP', array=np.array([1, 1, 1]), format='I')
    c4 = fits.Column(name='F_CHAN', array=np.array([1, 1, 1]), format='I')
    c5 = fits.Column(name='N_CHAN', array=np.array([3, 3, 3]), format='I')
    c6 = fits.Column(name='MATRIX', array=np.array([[1., 1., 1.], [1., 1., 1.], [1., 1., 1.]]), format='3D')

    matrix = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6])
    matrix.header.set('EXTNAME', 'MATRIX')

    primary_hdu = fits.PrimaryHDU()

    rmf2 = fits.HDUList([primary_hdu, matrix, ebounds])
    rmf2.writeto("rmf2_-1.fits", overwrite=True)
    rmf2.writeto("rmf2_1.fits", overwrite=True)

if __name__ == "__main__":
    main()
