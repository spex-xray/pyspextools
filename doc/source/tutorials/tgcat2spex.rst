TGCAT2Spex
==========

Tgcat2spex is a script to convert spectra from the Chandra TGCAT archive to SPEX format. Tgcat2spex works
with input flags from the command line. The '-h' flag shows the help of the tgcat2spex command::

    linux:~> tgcat2spex -h

A full overview of the arguments is given below in the section `Command-line arguments <tgcat2spex_commandline_>`_.

Example
-------

.. highlight:: none

Tgcat2spex detects the standard file names in a directory, so providing the path to the directory
should be enough. In addition, flags can be provided to, for example, overwrite existing spo and res
files and subtract the background::

    linux:~> tgcat2spex --overwrite --bkgsubtract /data/user/tgcat/obs_11387_tgid_3191
    ==================================
     This is tgcat2spex version 0.2.1
    ==================================

    Read source spectrum... OK
    Detected grating: Chandra LEG.
    Combining orders of the spectra... OK
    Convert to spo and write spo file... OK
    Reading response for order... -1  OK
    Reading response for order... -2  OK
    Reading response for order... -3  OK
    Reading response for order... -4  OK
    Reading response for order... -5  OK
    Reading response for order... -6  OK
    Reading response for order... -7  OK
    Reading response for order... -8  OK
    Reading response for order... 1  OK
    Reading response for order... 2  OK
    Reading response for order... 3  OK
    Reading response for order... 4  OK
    Reading response for order... 5  OK
    Reading response for order... 6  OK
    Reading response for order... 7  OK
    Reading response for order... 8  OK
    Reading effective area for order... -1  OK
    Reading effective area for order... -2  OK
    Reading effective area for order... -3  OK
    Reading effective area for order... -4  OK
    Reading effective area for order... -5  OK
    Reading effective area for order... -6  OK
    Reading effective area for order... -7  OK
    Reading effective area for order... -8  OK
    Reading effective area for order... 1  OK
    Reading effective area for order... 2  OK
    Reading effective area for order... 3  OK
    Reading effective area for order... 4  OK
    Reading effective area for order... 5  OK
    Reading effective area for order... 6  OK
    Reading effective area for order... 7  OK
    Reading effective area for order... 8  OK
    Write combined res file... OK

In this example, the directory contains a Chandra LETG spectrum with 16 orders. In the first step
the spectra from the pha2 file are combined and saved. After that, the responses and effective areas
are read in and combined into a single leg.spo and leg.res.

.. highlight:: python


.. _tgcat2spex_commandline:

Command-line arguments
----------------------

.. argparse::
   :filename: scripts/tgcat2spex
   :func: tgcat2spex_arguments
   :prog: tgcat2spex