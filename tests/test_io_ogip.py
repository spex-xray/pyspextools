import pytest
from pyspextools.io.ogip import OGIPRegion


class TestOGIPRegion:
    """
    Code Analysis

    Main functionalities:
    The OGIPRegion class is designed to handle the conversion of OGIP files (PHA, RMF, ARF, and CORR) to SPO and RES
    formats used by the SPEX software. It provides methods for reading in OGIP files, checking their compatibility,
    and converting them to SPO and RES formats. The class also includes a method for correcting possible shifts in
    the response array.

    Methods:
    - __init__(self): initializes the OGIPRegion object and sets default values for its fields
    - read_region(self, phafile, rmffile, bkgfile=None, arffile=None, corrfile=None, grouping=False): reads in OGIP
      files and converts them to SPO and RES formats
    - add_region(self, spec, resp, back=None, corr=None, area=None): adds OGIP files to the OGIPRegion object and
      converts them to SPO and RES formats
    - ogip_to_spex(self): converts OGIP files to SPO and RES formats
    - read_source_pha(self, phafile): reads in a PHA file for the source spectrum
    - read_background_pha(self, bkgfile): reads in a PHA file for the background spectrum
    - read_rmf(self, rmffile): reads in an RMF file for the response matrix
    - read_arf(self, arffile): reads in an ARF file for the effective area
    - read_corr(self, corrfile): reads in a CORR file for the correction spectrum
    - correct_possible_shift(self, ext): corrects possible shifts in the response array
    - check_ogip(self): checks the compatibility of the OGIP files
    - show_ogip(self): displays a summary of the OGIP information

    Fields:
    - spec: a Pha object representing the source spectrum
    - back: a Pha object representing the background spectrum
    - resp: an Rmf object representing the response matrix
    - area: an Arf object representing the effective area
    - corr: a Pha object representing the correction spectrum
    - input_spec: a boolean indicating whether a source spectrum has been input
    - input_back: a boolean indicating whether a background spectrum has been input
    - input_resp: a boolean indicating whether a response matrix has been input
    - input_area: a boolean indicating whether an effective area has been input
    - input_corr: a boolean indicating whether a correction spectrum has been input
    - first_channel_zero: a boolean indicating whether the first channel of the response matrix is zero
    - save_grouping: a boolean indicating whether to save grouping information in the SPO file
    """

    def test_read_region_path(self):
        """Tests that the read_region method successfully reads in all OGIP files."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', bkgfile='data/background.pha',
                           arffile='data/area.arf', corrfile='data/correction.pha', grouping=True)
        assert region.input_spec == True
        assert region.input_resp == True
        assert region.input_back == True
        assert region.input_area == True
        assert region.input_corr == True
        assert region.check_ogip() == 0

    def test_read_region_no_background_file(self):
        """Tests that the read_region method handles the case when no background file is specified."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', arffile='data/area.arf',
                           corrfile='data/correction.pha', grouping=True)
        assert region.input_spec == True
        assert region.input_resp == True
        assert region.input_back == False
        assert region.input_area == True
        assert region.input_corr == True

    def test_read_region_no_effective_area_file(self):
        """Tests that the read_region method handles the case when no effective area file is specified."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', bkgfile='data/background.pha',
                           corrfile='data/correction.pha', grouping=True)
        assert region.input_spec == True
        assert region.input_resp == True
        assert region.input_back == True
        assert region.input_area == False
        assert region.input_corr == True

    def test_read_region_no_correction_file(self):
        """Tests that the read_region method handles the case when no correction file is specified."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', bkgfile='data/background.pha',
                           arffile='data/area.arf', grouping=True)
        assert region.input_spec == True
        assert region.input_resp == True
        assert region.input_back == True
        assert region.input_area == True
        assert region.input_corr == False

    def test_read_region_invalid_input_objects(self):
        """Tests that the read_region method handles the case when input objects are not of the correct type."""
        region = OGIPRegion()
        with pytest.raises(Exception):
            region.add_region('source.pha', 'response.rmf', back='background.pha', corr='correction.pha',
                              area='area.arf')

    def test_ogip_to_spex_convert(self):
        """Tests that the ogip_to_spex method successfully converts OGIP files to spex format."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', bkgfile='data/background.pha',
                           arffile='data/area.arf', corrfile='data/correction.pha', grouping=True)
        stat = region.ogip_to_spex()
        assert region.res.check() == 0
        assert region.spo.check() == 0

    def test_ogip_to_spex_no_response(self):
        """Tests that the ogip_to_spex method handles the case when only a source and response are specified."""
        region = OGIPRegion()
        region.read_source_pha('data/source.pha')
        region.read_rmf('data/response.rmf')
        region.ogip_to_spex()
        assert region.res.check() == 0
        assert region.spo.check() == 0

    def test_ogip_to_spex_no_background_spectrum(self):
        """Tests that the ogip_to_spex method handles the case when no background spectrum is specified."""
        region = OGIPRegion()
        region.read_source_pha('data/source.pha')
        region.read_rmf('data/response.rmf')
        region.read_arf('data/area.arf')
        region.ogip_to_spex()
        assert region.res.check() == 0
        assert region.spo.check() == 0

    def test_ogip_to_spex_no_effective_area(self):
        """Tests that the ogip_to_spex method handles the case when no effective area is specified."""
        region = OGIPRegion()
        region.read_region('data/source.pha', 'data/response.rmf', bkgfile='data/background.pha',
                           corrfile='data/correction.pha', grouping=False)
        region.input_area = False
        assert region.ogip_to_spex() == 0
