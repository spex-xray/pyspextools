import pytest
from pyspextools.data.response import gaussrsp


class TestGaussrsp:
    #  Tests with valid input values for all parameters
    def test_valid_input(self):
        assert gaussrsp(-0.02, 0.0, 10.0, 0.0) == pytest.approx(0.0014334675273127038)
        assert gaussrsp(-0.01, 0.0, 10.0, 0.0) == pytest.approx(5.871482991872824)
        assert gaussrsp(0.01, 0.0, 10.0, 0.0) == pytest.approx(5.871482991872824)
        assert gaussrsp(0.02, 0.0, 10.0, 0.0) == pytest.approx(0.0014334675273127038)

    #  Tests with minimum valid input values for all parameters
    def test_minimum_input(self):
        assert gaussrsp(0.997, 1.0, 1.0, 0.0) == pytest.approx(1.3670611642004444e-08)
        assert gaussrsp(1.0, 1.0, 1.0, 0.0) == pytest.approx(939.4372786996514)
        assert gaussrsp(1.003, 1.0, 1.0, 0.0) == pytest.approx(1.3670611642004444e-08)

    #  Tests with fwhm_mu = 0
    def test_edge_case_fwhm_mu_zero(self):
        with pytest.raises(ValueError):
            gaussrsp(1.0, 1.0, -1.0, 1.0)

    #  Tests with sigma = 0
    def test_edge_case_sigma_zero(self):
        with pytest.raises(ValueError):
            gaussrsp(1.0, 1.0, 0.0, 1.0)
            gaussrsp(2.0, 1.0, 0.0, 1.0)
            gaussrsp(3.0, 1.0, 0.0, 1.0)
            gaussrsp(4.0, 1.0, 0.0, 1.0)

    #  Tests with dfwhm > 0 and dfwhm < 0
    def test_general_behaviour_dfwhm(self):
        assert gaussrsp(2.01, 2.0, 10.0, 1.0) == pytest.approx(8.636437274730676)
        assert gaussrsp(2.01, 2.0, 10.0, -1.0) == pytest.approx(3.404531843279669)
        assert gaussrsp(2.01, 2.0, 10.0, 2.0) == pytest.approx(11.415425692329116)
        assert gaussrsp(2.01, 2.0, 10.0, -2.0) == pytest.approx(1.5429090625281021)

    #  Tests with x = mu
    def test_general_behaviour_x_mu(self):
        assert gaussrsp(1.0, 1.0, 1.0, 0.0) == pytest.approx(939.4372786996514)

    #  Tests with x < mu
    def test_general_behaviour_x_less_than_mu(self):
        assert gaussrsp(0.99, 1.0, 10.0, 0.0) < gaussrsp(1.0, 1.0, 10.0, 0.0)

    #  Tests with x > mu
    def test_general_behaviour_x_greater_than_mu(self):
        assert gaussrsp(1.01, 1.0, 10.0, 0.0) < gaussrsp(1.0, 1.0, 10.0, 0.0)
