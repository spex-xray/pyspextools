Data filtering and optimization
===============================

Spectra and response matrices are not always delivered in their most optimal form. They, for example, contain
bad channels or channels with zero response. In addition, spectra and responses can be optimized for storage,
calculation speed and statistical accuracy. The pyspextools.data module contains functions to filter or optimize
spectra and response matrices with respect to their originals.

.. currentmodule:: pyspextools.data

Filtering for bad channels
--------------------------

The clean_region function returns a region without bad channels and zero response bins. The function reads the
original region object from the function input and returns a cleaned region. The function call is quite simple:

.. autofunction:: clean_region

The function first checks whether the input object is indeed an instance of the Region class and that the spectrum
and response are loaded. Then masks are created for several arrays in the spectrum and response files:

 * Chanmask is a boolean array, based on the 'used' array from the spo file, which identifies which spectral channels
   can be used or not. This logical value can be based on the Quality flag in the original OGIP spectrum. The channel
   should be usable if the channel is good in both the source and background spectrum.

 * Respmask identifies zero response values in the response array. They are found by looping through the response groups
   and through the channels (from ic1 to ic2, with a total of nc channels per group). If a channel has a zero response
   every time, it is also marked bad in the chanmask array (previous bullet). Then the zero response element is masked
   and the array indices (ic1, ic2 and nc) are modified to point to the correct response elements.

 * Groupmask masks response groups that have a zero response in total, so with no useful channels within the group.

When the masks are finished, they are applied to the input region, both to the spo and res component. The new
filtered region object is returned to the user. Such a call could look like this::

    filtered_region = clean_region(region)



