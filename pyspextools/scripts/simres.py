#!/usr/bin/env python

import os
import sys
import argparse
import pyspextools
from pyspextools.io.ogip import OGIPRegion
from pyspextools.data.badchannels import clean_region

import pyspextools.messages as message


def main():
    """The simres program generates a spo and res file from an input arf and rmf file, and optionally a background
    file. This is particularly useful for simulating spectra for future missions, where the source spectrum file is
    not supplied."""

    # Obtain command line arguments
    parser = simres_arguments()
    args = parser.parse_args()

    # Print message header
    message.print_header(os.path.basename(__file__))

    # Set color in the terminal
    message.set_color(args.color)

    # Load OGIP response files and background spectrum if provided
    ogipreg = OGIPRegion()

    # Read the background PHA file if specified:
    if args.bkgfile is not None:
        ogipreg.input_bkg = True
        ogipreg.read_background_pha(args.bkgfile)
        ogipreg.back.BackScaling = ogipreg.back.BackScaling / args.backscale
    else:
        ogipreg.input_bkg = False
        ogipreg.back = None

    # Corr spectrum is not used here
    ogipreg.corr = None

    # Read the response matrix
    ogipreg.read_rmf(args.rmffile)

    # Read the effective area
    if args.arffile is not None:
        ogipreg.input_area = True
        ogipreg.read_arf(args.arffile)
    else:
        ogipreg.input_area = False
        ogipreg.area = None

    # Generate dummy spectrum based on rmf channels
    ogipreg.spec.create_dummy(ogipreg.resp)

    # Convert spectra and responses to SPEX format
    stat = ogipreg.add_region(ogipreg.spec, ogipreg.resp, back=ogipreg.back, corr=ogipreg.corr, area=ogipreg.area)
    if stat != 0:
        sys.exit()

    # Filter for bad channels (if not blocked by command line argument)
    if args.badchan:
        ogipreg = clean_region(ogipreg)

    # Add the simres command to the file history
    history = []
    history.append("SIMRES version: {0}".format(pyspextools.__version__))
    command = ''
    for arg in sys.argv:
        command = command + ' ' + arg
    history.append("Command used: {0}".format(command))
    history.append("Variables derived from commandline:")
    for arg in vars(args):
        line = "{0} : {1}".format(arg, getattr(args, arg))
        history.append(line)

    # Check output file names
    spofile = ogipreg.spo.check_filename(args.spofile)
    resfile = ogipreg.res.check_filename(args.resfile)

    # Write output spo and res file
    print("Writing SPO to file: {0}".format(spofile))
    ogipreg.spo.write_file(spofile, exp_rate=args.exprate, overwrite=args.overwrite, history=history)

    print("Writing RES to file: {0}".format(resfile))
    ogipreg.res.write_file(resfile, overwrite=args.overwrite, history=history)


# Get command line arguments
def simres_arguments():
    """Obtain command line arguments."""
    parser = argparse.ArgumentParser(description=message.docs)
    parser.add_argument('--rmffile', help='Input Response matrix (required)', type=str, required=True)
    parser.add_argument('--bkgfile', help='Input Background spectrum', type=str)
    parser.add_argument('--arffile', help='Input Effective area file', type=str)
    parser.add_argument('--spofile', help='Output SPEX spectrum file (.spo, required)', type=str, required=True)
    parser.add_argument('--resfile', help='Output SPEX response file (.res, required)', type=str, required=True)
    parser.add_argument('--keep-badchannels', help='Do not remove bad channels.', dest="badchan", action="store_false",
                        default=True)
    parser.add_argument('--overwrite', help="Overwrite existing spo and res files with same name.", action="store_true",
                        default=False)
    parser.add_argument('--no-exprate', help="Do not write additional Exp_Rate column (SPEX <=3.04.00).",
                        dest='exprate', action="store_false", default=True)
    parser.add_argument('--backscale', help="Set a background scaling factor.", type=float, default=1.0)
    parser.add_argument('--no-color', help="Suppress color output.", dest="color", action="store_false", default=True)
    parser.add_argument('--version', action='version', version=message.version)

    return parser


if __name__ == "__main__":
    main()
