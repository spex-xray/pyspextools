.. _apec-example:

.. highlight:: none

APEC interface for SPEX
=========================

This example program creates an interface between ATOMDB/APEC and
the SPEX user model. Using this program, the APEC model can be used
within SPEX. 

Dependencies
------------

Before you start, make sure the following things are installed or set:

- Install numpy
- Install pyspextools (pip install pyspextools)
- Install pyatomdb (pip install pyatomdb) and import this into python once before use to install ATOMDB.
- Set the ATOMDB environment variable to your local ATOMDB installation (see also the ATOMDB installation instructions)::

    linux:~> export ATOMDB=/path/to/my/atomdb   (bash shell)
    linux:~> setenv ATOMDB /path/to/my/atomdb   (c shell)

For more information about installing ATOMDB and pyatomdb see `atomdb.org <http://www.atomdb.org/>`_ 

.. note:: pyATOMDB only supports Python 3 from version 0.6.0 onwards. If you are using Python 2,
          you need to install an older pyATOMDB version.

.. note:: This example apec.py script has been updated to work with pyATOMDB 0.8.0 and above.

Usage
-----

Use this program directly in the SPEX user model. Make the apec.py file executable before you start SPEX::

    linux:~> chmod u+x apec.py
    
If the apec.py is located in the working directory, it can be added to the user model easily::

    SPEX> par 1 1 exec av ./apec.py
    
If apec.py is located somewhere else, provide the full path::

    SPEX> par 1 1 exec av /path/to/apec.py        

The ATOMDB environment variable needs to be set to the ATOMDB installation at all times. 
Please note that by default, ATOMDB uses solar abundances by Anders & Grevesse (1989).

The SPEX user model also needs the number of parameters in the model. For APEC this needs to be set to 30::

    SPEX> par 1 1 npar v 30

The APEC model is now ready for use. See the table below for the parameter information.

Parameters
----------

User model parameter translation table:

+------+---------------+-----------------------------------------+
|Param |Variable       |Corresponding value and unit             |
|in    |in             |                                         |
|SPEX  |script         |                                         |
+======+===============+=========================================+
|p01   | usr.par[0]    |Normalisation (Photons m^-3 s^-1 keV^-1) |
+------+---------------+-----------------------------------------+
|p02   | usr.par[1]    |Temperature (keV)                        |
+------+---------------+-----------------------------------------+
|p03   | usr.par[2]    |                                         |
+------+---------------+-----------------------------------------+
|p04   | usr.par[3]    |                                         |
+------+---------------+-----------------------------------------+
|p05   | usr.par[4]    |                                         |
+------+---------------+-----------------------------------------+
|p06   | usr.par[5]    |06 C                                     |
+------+---------------+-----------------------------------------+
|p07   | usr.par[6]    |07 N                                     |
+------+---------------+-----------------------------------------+
|p08   | usr.par[7]    |08 O                                     |
+------+---------------+-----------------------------------------+
|p09   | usr.par[8]    |09 F                                     |
+------+---------------+-----------------------------------------+
|p10   | usr.par[9]    |10 Ne                                    |
+------+---------------+-----------------------------------------+
|p11   | usr.par[10]   |11 Na                                    |
+------+---------------+-----------------------------------------+
|p12   | usr.par[11]   |12 Mg                                    |
+------+---------------+-----------------------------------------+
|p13   | usr.par[12]   |13 Al                                    |
+------+---------------+-----------------------------------------+
|p14   | usr.par[13]   |14 Si                                    |
+------+---------------+-----------------------------------------+
|p15   | usr.par[14]   |15 P                                     |
+------+---------------+-----------------------------------------+
|p16   | usr.par[15]   |16 S                                     |
+------+---------------+-----------------------------------------+
|p17   | usr.par[16]   |17 Cl                                    |
+------+---------------+-----------------------------------------+
|p18   | usr.par[17]   |18 Ar                                    |
+------+---------------+-----------------------------------------+
|p19   | usr.par[18]   |19 K                                     |
+------+---------------+-----------------------------------------+
|p20   | usr.par[19]   |20 Ca                                    |
+------+---------------+-----------------------------------------+
|p21   | usr.par[20]   |21 Sc                                    |
+------+---------------+-----------------------------------------+
|p22   | usr.par[21]   |22 Ti                                    |
+------+---------------+-----------------------------------------+
|p23   | usr.par[22]   |23 V                                     |
+------+---------------+-----------------------------------------+
|p24   | usr.par[23]   |24 Cr                                    |
+------+---------------+-----------------------------------------+
|p25   | usr.par[24]   |25 Mn                                    |
+------+---------------+-----------------------------------------+
|p26   | usr.par[25]   |26 Fe                                    |
+------+---------------+-----------------------------------------+
|p27   | usr.par[26]   |27 Co                                    |
+------+---------------+-----------------------------------------+
|p28   | usr.par[27]   |28 Ni                                    |
+------+---------------+-----------------------------------------+
|p29   | usr.par[28]   |29 Cu                                    |
+------+---------------+-----------------------------------------+
|p30   | usr.par[29]   |30 Zn                                    |
+------+---------------+-----------------------------------------+
