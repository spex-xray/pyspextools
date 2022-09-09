#!/usr/bin/env python

# =========================================================
"""
Set the color theme of the module
"""
# =========================================================


class Colors:
    """This class contains the color codes needed to output colored text to the
    terminal. By default, colors are shown, but the user can request to output
    the text without color, either using a flag or manually setting the color
    scheme with the method below.

    :ivar HEADER: Color for headers.
    :vartype HEADER: str
    :ivar OKBLUE: Color blue.
    :vartype OKBLUE: str
    :ivar OKGREEN: Color green for OK.
    :vartype OKGREEN: str
    :ivar WARNING: Color yellow for Warnings.
    :vartype WARNING: str
    :ivar FAIL: Color red for Errors.
    :vartype FAIL: str
    :ivar ENDC: End character for color.
    :vartype ENDC: str
    :ivar BOLD: Bold font.
    :vartype BOLD: str
    :ivar UNDERLINE: Underline font.
    :vartype UNDERLINE: str
    """

    def __init__(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        self.BOLD = ''
        self.UNDERLINE = ''

        self.set_color(True)

    def set_color(self, setcol):
        """Set color output on (True) or off (False).

        :param setcol: Put color output on? (True/False)
        :type setcol: bool
        """

        if setcol:
            self.HEADER = '\033[95m'
            self.OKBLUE = '\033[94m'
            self.OKGREEN = '\033[92m'
            self.WARNING = '\033[93m'
            self.FAIL = '\033[91m'
            self.ENDC = '\033[0m'
            self.BOLD = '\033[1m'
            self.UNDERLINE = '\033[4m'
        else:
            self.HEADER = ''
            self.OKBLUE = ''
            self.OKGREEN = ''
            self.WARNING = ''
            self.FAIL = ''
            self.ENDC = ''
            self.BOLD = ''
            self.UNDERLINE = ''
