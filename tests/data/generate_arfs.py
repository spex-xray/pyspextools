#!/usr/bin/env python

from pyspextools.io import Arf
import numpy


def main():
    """This function generates the ARF files for the tests."""

    # Read success test
    arf = Arf()
    arf.LowEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.0
    arf.HighEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.1
    arf.EffArea = numpy.ones(100, dtype="float")
    arf.EnergyUnits = 'keV'
    arf.ARFUnits = 'cm2'
    arf.Order = 0
    arf.Grating = 0
    arffile = 'arf.arf'
    arf.write(arffile)

    # Read empty file
    arf = Arf()
    arf.LowEnergy = numpy.array([])
    arf.HighEnergy = numpy.array([])
    arf.EffArea = numpy.array([])
    arf.EnergyUnits = 'keV'
    arf.ARFUnits = 'cm2'
    arf.Order = 0
    arf.Grating = 0
    arffile = 'arf_empty.arf'
    arf.write(arffile)

    # Read ARF with missing keywords
    arf = Arf()
    arf.LowEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.0
    arf.HighEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.1
    arf.EffArea = numpy.ones(100, dtype="float")
    arffile = 'arf_missing_keywords.arf'
    arf.write(arffile)

    # Read ARF with missing keywords
    arf = Arf()
    arf.LowEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.0
    arf.HighEnergy = 0.1 * numpy.arange(100, dtype="float") + 1.1
    arf.EffArea = numpy.ones(100, dtype="float")
    arf.EffArea = numpy.where(arf.EffArea==1, numpy.nan, arf.EffArea)
    arf.EnergyUnits = 'keV'
    arf.ARFUnits = 'cm2'
    arffile = 'arf_nan.arf'
    arf.write(arffile)

if __name__ == "__main__":
   main()
