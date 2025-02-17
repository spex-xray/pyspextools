#!/usr/bin/env python

import os
import sys
import glob
import argparse
import astropy.io.fits as fits
import pyspextools
import pyspextools.io
from pyspextools.io.tg import TGRegion
from pyspextools.io.dataset import Dataset
from pyspextools.data.badchannels import clean_region

import pyspextools.messages as message


def main():
    """Program to convert Chandra grating spectra to SPEX format."""

    # Obtain command line arguments
    parser = tg2spex_arguments()
    args = parser.parse_args()

    # Print message header
    message.print_header(os.path.basename(__file__))

    # Set color in the terminal
    message.set_color(args.color)

    # Set the path from the command line
    path = args.path

    # Add the tg2spex command to the file history
    history = []
    history.append("TG2SPEX version: {0}".format(pyspextools.__version__))
    command = ''
    for arg in sys.argv:
        command = command + ' ' + arg
    history.append("Command used: {0}".format(command))
    history.append("Variables derived from commandline:")
    for arg in vars(args):
        line = "{0} : {1}".format(arg, getattr(args, arg))
        history.append(line)

    # Find out the origin of the observation (CIAO or TGCAT) and set filename mode.
    print("Origin of the observation is: ", end='')
    input_prefix = args.input_prefix

    # Check if default TGCAT filenames are there
    if os.path.isfile(path+"/pha2.gz"):
        tgcat = True
        phafile = path+"/pha2.gz"
        print("TGCAT")
    elif os.path.isfile(path+"/pha2"):
        tgcat = True
        phafile = path+"/pha2"
        print("TGCAT")
    # If not, start detecting the CIAO type file names ('prefix'_pha2.fits)
    else:
        tgcat = False
        print("CIAO")
        # Check if the input prefix is specified.
        if input_prefix != '':
            # If input prefix is specified
            if os.path.isfile(path+input_prefix+'pha2.fits'):
                # Is the suggested file there? If yes, save the name and path, and cheer.
                phafile = path+input_prefix+'pha2.fits'
                print("Found PHA2 file at: {0}".format(phafile))
            else:
                # If the file is not there, suggest to change the flag.
                message.error("Could not find file with name: {0}".format(path+input_prefix+'pha2.fits'))
                print("Please change the '--input-prefix flag to a correct name.")
                sys.exit()
        else:
            # If there is no prefix specified, do a detection
            filelist = glob.glob(path+"/*pha2.fits")
            if len(filelist) > 1:
                # If there are more pha2 files, ask for a more detailed specification.
                message.error("More than one pha2 files found. Please provide the input prefix through the "
                              "'--input-prefix' flag.")
                sys.exit()
            elif len(filelist) == 1:
                # If there is one pha2 file, this is probably the right one:
                phafile = filelist[0]
                print("Found PHA2 file at: {0}".format(phafile))
                # Deduce input_prefix from
                input_prefix = phafile.replace(path+"/", '')
                input_prefix = input_prefix.replace('pha2.fits', '')
                print("Autodetected input file prefix to be: {0}".format(input_prefix))
            else:
                # If there is no pha2 file, we are obviously looking in the wrong place.
                message.error("No PHA2 file found at this path. Check your input.")
                sys.exit()

    # Read the data and header of the PHA2 file to get the origin right
    (phadata, phaheader) = fits.getdata(phafile, 'SPECTRUM', header=True)

    # Detected instrument and gratings
    print("Autodetected mission and instruments:")
    print("Mission:  {0}".format(phaheader['TELESCOP']))
    print("Grating:  {0}".format(phaheader['GRATING']))
    print("Detector: {0}".format(phaheader['INSTRUME']))

    # Do the conversion from PHA2 to SPEX format for each grating
    dataset = Dataset()

    if phaheader['GRATING'] == 'HETG':
        hetg = TGRegion()
        metg = TGRegion()

        # Obtain rmf and arf file list for hetg and metg
        print("Start HETG file conversion:")
        (heg_rmf_list, heg_arf_list) = search_response_files(path, tgcat, input_prefix, 'heg')
        if len(heg_rmf_list) == 0:
            message.error("HETG response list generation failed.")
            sys.exit()
        stat = hetg.read_region(phafile, heg_rmf_list, heg_arf_list, 'HETG', bkgsubtract=args.bkgsubtract)
        if stat != 0:
            message.error("HETG conversion failed")
            sys.exit()

        # Clean bad channels
        if args.badchan:
            print("Clean bad channels for HETG:")
            hetg = clean_region(hetg)

        dataset.append_region(hetg, 1, 1)

        print("Start METG file conversion:")
        (meg_rmf_list, meg_arf_list) = search_response_files(path, tgcat, input_prefix, 'meg')
        if len(meg_rmf_list) == 0:
            message.error("METG response list generation failed.")
            sys.exit()
        stat = metg.read_region(phafile, meg_rmf_list, meg_arf_list, 'METG', bkgsubtract=args.bkgsubtract)
        if stat != 0:
            message.error("METG conversion failed")
            sys.exit()

        # Clean bad channels

        if args.badchan:
            print("Clean bad channels for METG:")
            metg = clean_region(metg)

        dataset.append_region(metg, 1, 2)

    elif phaheader['GRATING'] == 'LETG':

        letg = TGRegion()

        # Obtain rmf and arf file list for letg
        print("Start LETG file conversion:")
        (leg_rmf_list, leg_arf_list) = search_response_files(path, tgcat, input_prefix, 'leg')
        if len(leg_rmf_list) == 0:
            message.error("LETG response list generation failed.")
            sys.exit()
        stat = letg.read_region(phafile, leg_rmf_list, leg_arf_list, 'LETG', bkgsubtract=args.bkgsubtract)
        if stat != 0:
            message.error("LETG conversion failed")
            sys.exit()

        # Clean bad channels
        if args.badchan:
            print("Clean bad channels for LETG:")
            letg = clean_region(letg)

        dataset.append_region(letg, 1, 1)

    else:
        message.error("Grating name not recognized.")
        sys.exit()

    # Set the file names for the res and spo file.
    if args.output_prefix == '':
        args.output_prefix = phaheader['GRATING']
    spofile = args.output_prefix+'.spo'
    resfile = args.output_prefix+'.res'

    # Write regions to file
    message.proc_start("Write spectra and response to SPEX format")
    stat = dataset.write_all_regions(spofile, resfile, exp_rate=args.exprate, overwrite=args.overwrite, history=history)
    message.proc_end(stat)


# Search RMF and ARF files for certain grating
def search_response_files(path, tgcat, prefix, gname):
    """Search the accompanying response file for a certain grating. gname can be 'heg', 'meg' or 'leg'."""

    if tgcat:
        rmflist = glob.glob(path+'/'+gname+'*.rmf.gz')
        arflist = glob.glob(path+'/'+gname+'*.arf.gz')
    else:
        rmflist = glob.glob(path+'/'+prefix+gname+'*.rmf')
        arflist = glob.glob(path+'/'+prefix+gname+'*.arf')
        if len(rmflist) <= 0 or len(arflist) <= 0:
            rmflist = glob.glob(path+'/tg/'+prefix+gname+'*.rmf')
            arflist = glob.glob(path+'/tg/'+prefix+gname+'*.arf')

    if len(rmflist) <= 0 or len(arflist) <= 0:
        message.error("Could not find suitable rmf or arf files in path.")
        print("We suggest to run the 'mktgresp' task from CIAO to obtain all the responses.")

    rmflist.sort()
    arflist.sort()

    return rmflist, arflist


# Get command line arguments
def tg2spex_arguments():
    """Obtain command line arguments."""
    parser = argparse.ArgumentParser(description=message.docs)
    parser.add_argument('path', help="Path to the observation directory where the pha2, arfs and rmfs are.")
    parser.add_argument('--input-prefix', help="Input filename prefix (example: 'hrcf04149_repro_').",
                        dest="input_prefix", default='')
    parser.add_argument('--output-prefix', help="Output filename prefix (names the output to 'prefix'leg.spo/res",
                        dest="output_prefix", default='')
    parser.add_argument('--no-bkgsubtract', help="Substract the background spectrum.", dest="bkgsubtract",
                        action="store_false", default=True)
    parser.add_argument('--keep-badchannels', help='Do not remove bad channels.', dest="badchan", action="store_false",
                        default=True)
    parser.add_argument('--overwrite', help="Overwrite existing spo and res files with same name.", action="store_true",
                        default=True)
    parser.add_argument('--no-exprate', help="Do not write additional Exp_Rate column (SPEX <=3.04.00).",
                        dest="exprate", action="store_false", default=True)
    parser.add_argument('--no-color', help="Suppress color output.", dest="color", action="store_false", default=True)
    parser.add_argument('--version', action='version', version=message.version)

    return parser


if __name__ == "__main__":
    main()
