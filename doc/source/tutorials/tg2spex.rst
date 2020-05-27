.. _tg2spex:

TG2Spex - Convert Chandra grating data
======================================

Tg2spex is a script to convert spectra from Chandra grating observations to SPEX format. Tg2spex works
with input flags from the command line. The '-h' flag shows the help of the tg2spex command::

    linux:~> tg2spex -h

A full overview of the arguments is given below in the section `Command-line arguments <tg2spex_commandline_>`_.

Example
-------

.. highlight:: none

Tg2spex detects the standard file names in a directory, so providing the path to the directory
should be enough. In addition, flags can be provided to, for example, overwrite existing spo and res
files::

    linux:~> tg2spex --overwrite /data/user/tgcat/obs_11387_tgid_3191
    ==================================
     This is tg2spex version 0.2.1
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


.. _tg2spex_commandline:

Command-line arguments
----------------------

.. argparse::
   :filename: scripts/tg2spex
   :func: tg2spex_arguments
   :prog: tg2spex