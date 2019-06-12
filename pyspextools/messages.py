#!/usr/bin/env python

# =========================================================
"""
Methods to send messages to the user.
"""
# =========================================================

# Stuff to import for compatibility between python 2 and 3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import pyspextools
from pyspextools.color import Colors

# Stuff to import for compatibility between python 2 and 3

from future import standard_library

standard_library.install_aliases()

# Set general messages for argument parsing
docs = 'See full documentation at: https://spex-xray.github.io/pyspextools'
version = '%(prog)s {:s} (C) 2018-2019, Jelle de Plaa, SRON Netherlands Institute for Space Research, ' \
          'Apache 2.0 License'.format(pyspextools.__version__)

# Initialize colors
color = Colors()

def set_color(set):
    '''Set whether text output can be colored or not.'''
    if set:
        color.set_color(True)
    else:
        color.set_color(False)

# Create methods to do show processes and their result
def proc_start(text):
    '''Print text to terminal at the start of the procedure.'''
    print(text+'... ', end='')
    sys.stdout.flush()

def proc_end(result):
    '''Report the result of a procedure to terminal.'''
    if result == 0:
        print(color.OKGREEN+"OK"+color.ENDC)
    else:
        print(color.FAIL+"FAILED"+color.ENDC)

# Print a warning to screen
def warning(text):
    print(color.WARNING+"WARNING "+color.ENDC+text)

def error(text):
    print(color.FAIL+"ERROR "+color.ENDC+text)

def print_header(scriptname):
    '''Print the header when executing a script.'''
    print("==================================")
    print(" This is {:s} version {:s}".format(scriptname, pyspextools.__version__))
    print("==================================")
    print("(C) 2018-2019 Jelle de Plaa")
    print("SRON Netherlands Institute for Space Research")
    print("Github: https://github.com/spex-xray/pyspextools")
    print("")

