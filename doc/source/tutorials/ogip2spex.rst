OGIP2spex
=========

OGIP2spex is a script that converts OGIP spectra and responses to SPEX format, similar to the trafo program in SPEX.

The ogip2spex works with command-line arguments to gather all the input, contrary to trafo, which asks questions
interactively. When pyspex is installed, the ogip2spex program can show an overview of the available command-line
arguments directly from the command line::

    ogip2spex -h

A full overview of the arguments is given below in the section `Command-line arguments <ogip2spex_commandline_>`_.

.. NOTE::
   By default ogip2spex creates spo files without the 'Ext_Rate' column. This column was added in SPEX version 3.05.00.
   The Ext_Rate column contains the ratio between the backscale values of the source and background spectrum and is
   used to properly simulate spectra. If you need to simulate spectra including background, then make sure the Ext_Rate
   column is created.

Example
-------

.. highlight:: none

Suppose one would like to convert a set of OGIP spectra from the MOS instrument aboard XMM-Newton. The XMM-Newton SAS
software has provided a *M1.pi* file with the source spectrum, *M1_bkg.pi* with the source background, *M1.rmf*
containing the response matrix and *M1.arf* with the effective area. These files can be converted into SPEX format
within one go::

    linux:~> ogip2spex --phafile M1.pi --bkgfile M1_bkg.pi --rmffile M1.rmf --arffile M1.arf --spofile M1.spo --resfile M1.res

The output starts by listing and checking the input OGIP files::

    ==================================
     This is ogip2spex version 0.2
    ==================================

    Input PHA file: M1.pi
    Input Background file: M1_bkg.pi
    Input Response file: M1.rmf
    Input Effective area file: M1.arf
    Check OGIP source spectrum... OK
    Check OGIP background spectrum... OK
    Check OGIP response matrix... OK
    Check OGIP effective area file... OK

Then the program converts the OGIP files to SPEX format::

    Convert OGIP spectra to spo format... WARNING Lowest channel boundary energy is 0. Set to 1E-5 to avoid problems.
    OK
    Convert OGIP response to res format... OK

In this case, the lowest energy boundary of the first channel of the MOS spectrum is 0, which SPEX does not like. Since
this bin is not used, it does not hurt to change this zero into a small number (smaller than the upper boundary), in
this case 1E-5.

The program continues with detecting bad channels in the spectrum and channels with zero response in the response
matrix::

    Identify bad channels in spectrum and response matrix and re-index matrix... OK
    Number of good channels: 795
    Number of bad channels:  5
    Removing bad channels from spectral region... OK
    Number of original groups:       2394
    Number of zero-response groups:  0
    Number of original response elements:  1000056
    Number of bad response elements:       0
    Removing bad channels from response matrix... OK

The removal of bad channels is default behavior. In cases where the bad channels should be kept, one can add the
'--keep-badchannels' argument to the call to ogip2spex.

At the end of the program, the spo and res files are saved::

    Writing SPO to file: M1.spo
    Writing RES to file: M1.res

One can overwrite existing files by adding the '--overwrite' option to the ogip2spex call.

This spo file does not have an 'Ext_Rate' column. To generate a spo file with such a column, add '--extrate' to the
ogip2spex call.

By default, ogip2spex shows colored output for warnings, errors and OKs. If it is hard for you to see, use the
'--no-color' argument to show the output without colors.

.. highlight:: python

.. _ogip2spex_commandline:

Command-line arguments
----------------------

.. argparse::
   :filename: scripts/ogip2spex
   :func: ogip2spex_arguments
   :prog: ogip2spex