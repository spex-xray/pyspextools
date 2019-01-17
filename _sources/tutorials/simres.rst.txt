.. _simres:

SIMRES
======

Simres is a script to create a SPEX format spo and res file from just an input response file, optionally with an
effective area file (ARF) and background spectrum. This is very useful to create spo and res files
for future missions, where only responses and effective area files are provided. The spo and res files can be used
to simulate spectra in SPEX.

The parameters of simres can be shown on the command line by the '-h' flag::

    simres -h

Example
-------

.. highlight:: none

Suppose we have a response matrix from a future instrument like X-IFU aboard Athena called athena_xifu_A.rsp, then
we can create a spo and res file with the simres command, and call them xifu.spo and xifu.res::

    linux:~> simres --rmffile athena_xifu_A.rsp --spofile xifu.spo --resfile xifu.res
    ==================================
     This is simres version 0.2.2
    ==================================

    Read RMF response matrix... WARNING This is an RSP file with the effective area included.
    Do not read an ARF file, unless you know what you are doing.
    OK
    Check OGIP source spectrum... OK
    Check OGIP response matrix... OK
    Convert OGIP spectra to spo format... OK
    Convert OGIP response to res format... OK
    Identify bad channels in spectrum and response matrix and re-index matrix... OK
    Number of good channels: 29600
    Number of bad channels:  0
    Removing bad channels from spectral region... OK
    Number of original groups:       29600
    Number of zero-response groups:  0
    Number of original response elements:  8898275
    Number of bad response elements:       0
    Removing bad channels from response matrix... OK
    Writing SPO to file: xifu.spo
    Writing RES to file: xifu.res

In this case, an RSP file is provided, which should contain the effective area already. The program issues a warning,
because usually also separate arf files are provided. This warning cautions the user to not apply the effective area
correction twice.

The output spectrum is obviously wrong with a constant count rate across the entire band. The idea is to set up a new
model in SPEX and simulate a new spectrum with this response matrix to replace the dummy spectrum with something more
realistic.

.. highlight:: python

Command-line arguments
----------------------

.. argparse::
   :filename: scripts/simres
   :func: simres_arguments
   :prog: simres
