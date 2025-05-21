# Pyspextools change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-02-18

### Changed
 
 - Move to pyproject.toml file to build and install pyspextools
 - Determine PHA type in cases when HDUCLAS3 keyword is not defined

## [0.6.1]

### Fixed
 
 - Fixed an issue with large XRISM response matrices where the second matrix 
   extension was not properly converted.

## [0.6.0]

### Added
 
 - Added a force_poisson option to PHA reading routine and ogip2spex for cases where other
   types of statistics are used and Poisson is desired.
 - Added code to fix bins with zero width in ROSAT response matrices.
 - Added tutorial about how to create .spo and .res files with more complicated sectors and regions.

### Fixed
 
 - Fixed ogipgenrsp which now uses the rmf structure with multiple MATRIX extensions.

## [0.5.0]

### Changed

 - SPEX spectra and responses are now written in double precision.

### Fixed

 - Fix for converting spectra from LEM and HEX-P responses where channel numbers are shifted by 1.
 - Fix for converting spectra from rgscombine.

### Removed

 - Discontinued Python 2 support.


## [0.4.0] 

### Added

 - Added capability to read and convert OGIP RMF files with multiple MATRIX extensions.

### Changed

 - Updated apec.py to work with pyatomdb 0.8.0 and above.

## [0.3.4]

### Changed

 - Consistently changed pyspex to pyspextools in anticipation of the pyspex release with SPEX 3.06.00.
   (Thanks to Anna Ogorzałek for reporting these issues).

### Fixed

 - Fixed issue with reading multiple res and spo files.

## [0.3.2]

### Added

 - Added no-area option to the ogipgenrsp script.

### Changed

 - Updated apec.py example script for pyATOMDB >= 0.6.0 (only supports Python 3 now).
   (Thanks to Francois Mernier for reporting.)
 
## [0.3.1]

### Added

 - Produce an error message in rare cases where all detector channels are bad.

### Fixed

 - Fixed issue reading PHA files without HDUCLAS2 and HDUCLAS3 keywords.
 - Fixed issue with using setup.py on Python 2.

## [0.3.0]

### Added

 - Initial release of pyspextools
