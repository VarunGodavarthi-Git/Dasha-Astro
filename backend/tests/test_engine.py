from datetime import date, time

import pytest

from app.engine import CityLookupError, GeocodedCity, build_chart_from_coordinates, geocode_city
from app.engine import _varga_position


class EmptyGeocoder:
    def geocode(self, *_args, **_kwargs):
        return None


def test_invalid_city_raises_clear_error():
    with pytest.raises(CityLookupError):
        geocode_city("NotARealCityNameForThisDemo", "test-agent", geocoder=EmptyGeocoder())


def test_build_chart_from_coordinates_has_core_payload():
    city = GeocodedCity(
        query="Tanuku",
        display_name="Tanuku, Andhra Pradesh, India",
        latitude=16.7547,
        longitude=81.6814,
        timezone="Asia/Kolkata",
    )

    chart = build_chart_from_coordinates(date(1994, 8, 1), time(6, 30), city)

    assert chart["calculation"]["ayanamsha"] == "True Chitra Paksha Lahiri"
    assert chart["calculation"]["node"] == "True Node"
    assert chart["birth"]["timezone"] == "Asia/Kolkata"
    assert chart["lagna"]["name"] == "Lagna"
    assert len(chart["planets"]) == 9
    assert len(chart["houses"]) == 12
    assert chart["vargas"]["D9"]["lagna"]["house"] == 1
    assert chart["vargas"]["D10"]["lagna"]["house"] == 1


def test_dashamsha_uses_parashari_odd_even_counting():
    # Mesha is an odd sign, so the first Dashamsha starts from Mesha itself.
    assert _varga_position(0.5, "D10")["rashi"] == "Mesha"
    assert _varga_position(6.5, "D10")["rashi"] == "Mithuna"

    # Vrishabha is an even sign, so the first Dashamsha starts from the 9th sign, Makara.
    assert _varga_position(30.5, "D10")["rashi"] == "Makara"
    assert _varga_position(36.5, "D10")["rashi"] == "Meena"

    # Tula is an odd sign; a Lagna in the 3rd tenth of Tula must land in Dhanu.
    assert _varga_position(186.5, "D10")["rashi"] == "Dhanu"


def test_jagannatha_hora_pdf_reference_positions():
    city = GeocodedCity(
        query="Tanuku JHora PDF",
        display_name="Tanuku, India",
        latitude=16.75,
        longitude=81.7,
        timezone="Asia/Kolkata",
    )

    chart = build_chart_from_coordinates(date(1999, 10, 1), time(6, 9), city)
    bodies = {"Lagna": chart["lagna"]} | {planet["name"]: planet for planet in chart["planets"]}
    d9 = {"Lagna": chart["vargas"]["D9"]["lagna"]} | {
        planet["name"]: planet for planet in chart["vargas"]["D9"]["planets"]
    }

    # Reference: C:\Users\Varun\Downloads\VarunJagannatha Astro.pdf, page 1.
    # JHora node values in that PDF match Mean Node, while Dasha Astro intentionally uses True Node.
    expected = {
        "Lagna": ("Kanya", _dms_to_degree(16, 31, 30.57), "Vrishabha"),
        "Sun": ("Kanya", _dms_to_degree(13, 34, 15.21), "Vrishabha"),
        "Moon": ("Vrishabha", _dms_to_degree(28, 32, 36.06), "Kanya"),
        "Mars": ("Vrischika", _dms_to_degree(24, 49, 26.93), "Kumbha"),
        "Mercury": ("Kanya", _dms_to_degree(29, 54, 45.73), "Kanya"),
        "Jupiter": ("Mesha", _dms_to_degree(8, 58, 54.92), "Mithuna"),
        "Venus": ("Simha", _dms_to_degree(1, 39, 30.34), "Mesha"),
        "Saturn": ("Mesha", _dms_to_degree(22, 27, 56.46), "Tula"),
    }

    for name, (rashi, degree, navamsha) in expected.items():
        assert bodies[name]["rashi"] == rashi
        assert bodies[name]["degree_in_rashi"] == pytest.approx(degree, abs=1 / 60)
        assert d9[name]["rashi"] == navamsha


def _dms_to_degree(degrees: int, minutes: int, seconds: float) -> float:
    return degrees + minutes / 60 + seconds / 3600
