#!/usr/bin/env python


class ColorCodes:
    """Set the color theme of the module."""
    color_codes = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    def __init__(self):
        self.set_color(True)

    def set_color(self, setcol):
        """If setcol is True, enable showing terminal colors. False disables the colors."""
        if not isinstance(setcol, bool):
            raise TypeError("The setcol parameter should be either True or False.")
        if setcol:
            for code, value in ColorCodes.color_codes.items():
                setattr(ColorCodes, code, value)
        else:
            for code in ColorCodes.color_codes.keys():
                setattr(ColorCodes, code, '')
