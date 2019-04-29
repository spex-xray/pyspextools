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
from pyspextools.color import Colors

# Stuff to import for compatibility between python 2 and 3

from future import standard_library

standard_library.install_aliases()

color = Colors()

def set_color(set):
    if set:
        color.set_color(True)
    else:
        color.set_color(False)

# Create methods to do show processes and their result
def proc_start(text):
    print(text+'... ', end='')
    sys.stdout.flush()

def proc_end(result):
    if result == 0:
        print(color.OKGREEN+"OK"+color.ENDC)
    else:
        print(color.FAIL+"FAILED"+color.ENDC)

# Print a warning to screen
def warning(text):
    print(color.WARNING+"WARNING "+color.ENDC+text)

def error(text):
    print(color.FAIL+"ERROR "+color.ENDC+text)

