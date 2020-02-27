Managing datasets in pyspextools
================================

The best starting point to manipulate SPEX files is to use the Dataset class in pyspextools. A dataset can be a
collection of several spectrum-response combinations, which are called regions. This way, multiple related spectra can
be stored in a spo and res file.

The different spectra and responses inside a dataset can be related to each other in multiple ways. To distinguish
between different cases, each spectrum-response combination can have a sector and region number. These numbers are
defined as follows:

**Sector**
    A sector number refers to the model that needs to be associated to the dataset. Suppose one has spectra from two
    areas of the sky that share a common absorption component, but have different emission components. One would like
    to fit these spectra simultaneously with coupled absorption components. The SPEX solution is to assign different
    sector numbers to the different spectra, such that SPEX applies the right models to the right dataset.

**Region**
    A region number identifies the dataset that a model applies to. Usually the region number just iterates over the
    number of spectra, so four spectra are just counted as 1, 2, 3 and 4.

However, in some cases it can be helpful to point different sectors to one region. For example, a particle background
model is not supposed to be multiplied by the effective area, but just the response. Then this model needs to be added
to the model spectrum of the previous region. In that case, two spectrum-response combinations are required (one with
and one without ARF), where each combination obtains its own sector number (1,2), but only a single region number(1).
See the `SPEX Cookbook <http://var.sron.nl/SPEX-doc/cookbookv3.0/cookbookch8.html#x36-570008>`_ for more information.

Example use of the dataset class
--------------------------------

Let's perform a simple operation to read a few existing spo and res files and combine them into one dataset.
First, start python and then import the pyspextools.io module::

    >>> import pyspextools.io

The pyspextools.io module contains a Dataset class that needs to be initiated first::

    >>> data = pyspextools.io.Dataset()

The Dataset class contains methods to read spo and res files into a region. Suppose we have two spectra from the
RGS instrument aboard XMM-Newton. We have two sets of spectra and responses: RGS1.spo, RGS1.res, RGS2.spo and RGS2.res.
We can read them into the dataset easily using the read_all_regions method::

    >>> data.read_all_regions("RGS1.spo","RGS1.res")
    >>> data.read_all_regions("RGS2.spo","RGS2.res")

This method reads all regions within a file and adds it to the dataset. In this case, the spectral files only contain
one region, so by reading them in both, we have now two parts of the dataset::

    >>> data.show()
    ===========================================================
     Part 1
    ===========================================================
     Sector:            1  =>  Region:            1
     Label:
     --------------------  Spectrum  -------------------------
     Original spo file                      :  RGS1.spo
     Number of data channels                :  2831
     Data energy range                      :  0.32 - 2.41 keV
     Exposure time mean                     :  104813.48 s
     --------------------  Response  -------------------------
     Original response file name            :  RGS1.res
     Number of data channels in response    :  2831
     Number of response components          :  8

    ===========================================================
     Part 2
    ===========================================================
     Sector:            1  =>  Region:            2
     Label:
     --------------------  Spectrum  -------------------------
     Original spo file                      :  RGS2.spo
     Number of data channels                :  2728
     Data energy range                      :  0.33 - 2.64 keV
     Exposure time mean                     :  104409.24 s
     --------------------  Response  -------------------------
     Original response file name            :  RGS2.res
     Number of data channels in response    :  2728
     Number of response components          :  8



Suppose one wants to apply a different model for RGS2 than for RGS1 and put RGS2 in a different sector, then we can do
that as follows::

    >>> data.assign_sector(2,2)
    >>> data.show()
    ===========================================================
     Part 1
    ===========================================================
     Sector:            1  =>  Region:            1
     Label:
     --------------------  Spectrum  -------------------------
     Original spo file                      :  RGS1.spo
     Number of data channels                :  2831
     Data energy range                      :  0.32 - 2.41 keV
     Exposure time mean                     :  104813.48 s
     --------------------  Response  -------------------------
     Original response file name            :  RGS1.res
     Number of data channels in response    :  2831
     Number of response components          :  8

    ===========================================================
     Part 2
    ===========================================================
     Sector:            2  =>  Region:            2
     Label:
     --------------------  Spectrum  -------------------------
     Original spo file                      :  RGS2.spo
     Number of data channels                :  2728
     Data energy range                      :  0.33 - 2.64 keV
     Exposure time mean                     :  104409.24 s
     --------------------  Response  -------------------------
     Original response file name            :  RGS2.res
     Number of data channels in response    :  2728
     Number of response components          :  8

In the data.show() command, the part with the RGS2 spectrum (Part 2) has now sector 2 assigned to it. We can now save
the created structure to one spo and res file::

    >>> data.write_all_regions("RGS.spo","RGS.res")

The dataset has been successfully written to RGS.spo and RGS.res.
