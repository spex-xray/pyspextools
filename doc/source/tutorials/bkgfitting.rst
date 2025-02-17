.. _bkgfitting:

How to create SPEX files for background fitting
===============================================

In this example, we are using pyspextools to build a .spo and .res file suitable for
fitting instrumental and particle background simultaneously with fitting the source
spectrum. We do this by reading in the source spectrum twice. During the first read,
we read in both the RMF and ARF file. This is to model the photons from the sky.
During the second read, we just read in the source spectrum and RMF. This way,
the effective area of the mirror is not applied, so only the redistribution
function is used.

The files used in this example are:
     * M1_1.pi : The source spectrum from XMM-Newton MOS1.
     * M1_1.rmf : The response matrix from XMM-Newton MOS1.
     * M1_1.arf : The effective area from XMM-Newton MOS1.

First import the pyspextools classes :ref:`ogipregion_class` and :ref:`dataset_class`
needed for this example::

    from pyspextools.io.ogip import OGIPRegion
    from pyspextools.io.dataset import Dataset

Reading the spectrum the first time (for source modeling). The ``read_region``
function automatically converts the region to SPEX format in the background::

    m1_source = OGIPRegion()
    m1_source.read_region("M1_1.pi", "M1_1.rmf", arffile="M1_1.arf")

Reading the spectrum for the second time (for instrumental and particle background modeling)::

    m1_back = OGIPRegion()
    m1_back.read_region("M1_1.pi", "M1_1.rmf")

Now we have two region objects. The first one for the source and the second one for the background.
To model the background separately and add the background model to the source model when fitting,
we need to set up two sectors (model sets). The first sector will contain the model components for the
X-ray photons from the sky and the second sector the background models. The models themselves will
be defined later in SPEX. But, we need to configure the response file such that the spectrum from
sector 2 is folded with the RMF only and then applied to the spectrum in region 1. We can set this
when combining our regions into a SPEX dataset::

    spex_data = Dataset()
    spex_data.append_region(m1_source, 1, 1)
    spex_data.append_region(m1_back, 2, 1)

The second and third arguments of ``append_region`` contain the sector number and region number respectively.
Once we have appended the regions to the SPEX dataset, we can write it to file::

    spex_data.write_all_regions("M1_example.spo", "M1_example.res", overwrite=True)

You should now have a .spo and .res file that is ready for particle background fitting.
