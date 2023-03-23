#!/usr/bin/env python

# =========================================================
"""
Methods to send messages to the user.
"""
# =========================================================

import sys
import pyspextools
from pyspextools.color import Colors

# Set general messages for argument parsing
docs = 'See full documentation at: https://spex-xray.github.io/pyspextools'
version = '%(prog)s {:s} (C) 2018-2023, Jelle de Plaa, SRON Netherlands Institute for Space Research, ' \
          'Apache 2.0 License'.format(pyspextools.__version__)

# Initialize colors
color = Colors()


def set_color(setcol):
    """Set whether text output can be colored or not.

    :param setcol: Set colored text output? (True/False)
    :type setcol: bool
    """

    if setcol:
        color.set_color(True)
    else:
        color.set_color(False)


# Create methods to do show processes and their result
def proc_start(text):
    """Print text to terminal at the start of the procedure.

    :param text: Text to print in front of result.
    :type text: str
    """

    print(text+'... ', end='')
    sys.stdout.flush()


def proc_end(result):
    """Report the result of a procedure to terminal.

    :param result: Returned error code by program. Successful execution returns 0.
    :type result: int
    """

    if result == 0:
        print(color.OKGREEN+"OK"+color.ENDC)
    else:
        print(color.FAIL+"FAILED"+color.ENDC)


# Print a warning to screen
def warning(text):
    """Print a warning text.

    :param text: Warning text to print.
    :type text: str
    """

    print(color.WARNING+"WARNING "+color.ENDC+text)


def error(text):
    """Print an error text.

    :param text: Error text to print.
    :type text: str
    """

    print(color.FAIL+"ERROR "+color.ENDC+text)


def print_header(scriptname):
    """Print the header when executing a script.

    :param scriptname: Name of the script being executed.
    :type scriptname: str
    """
    print("==================================")
    print(" This is {:s} version {:s}".format(scriptname, pyspextools.__version__))
    print("==================================")
    print("(C) 2018-2023 Jelle de Plaa")
    print("SRON Netherlands Institute for Space Research")
    print("Github: https://github.com/spex-xray/pyspextools")
    print("")
