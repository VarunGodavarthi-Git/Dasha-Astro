from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from .dasha import calculate_dasha
from .location import CityLookupError, GeocodedCity, geocode_city


class AstrologyCalculationError(RuntimeError):
    pass


RASHIS = [
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrischika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
]

NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
}

AYANAMSHA_MODE = swe.SIDM_TRUE_CITRA
AYANAMSHA_NAME = "True Chitra Paksha Lahiri"
PLANET_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
NODE_TROPICAL_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
HOUSE_FLAGS = swe.FLG_SIDEREAL


def calculate_vedic_chart(
    birth_date: date,
    birth_time: time,
    city_name: str,
    user_agent: str,
) -> dict[str, Any]:
    geocoded = geocode_city(city_name, user_agent=user_agent)
    return build_chart_from_coordinates(
        birth_date=birth_date,
        birth_time=birth_time,
        city=geocoded,
    )


def build_chart_from_coordinates(
    birth_date: date,
    birth_time: time,
    city: GeocodedCity,
) -> dict[str, Any]:
    try:
        local_dt = datetime.combine(birth_date, birth_time).replace(tzinfo=ZoneInfo(city.timezone))
    except Exception as exc:
        raise AstrologyCalculationError(f"Invalid timezone for city: {city.timezone}") from exc

    utc_dt = local_dt.astimezone(timezone.utc)
    hour_decimal = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600 + utc_dt.microsecond / 3_600_000_000

    try:
        swe.set_sid_mode(AYANAMSHA_MODE, 0, 0)
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal, swe.GREG_CAL)
        ayanamsha_value = _ayanamsha_value(jd_ut)
        planets = _planet_positions(jd_ut, PLANET_FLAGS, ayanamsha_value)
        houses = _house_cusps(jd_ut, city.latitude, city.longitude)
    except Exception as exc:
        raise AstrologyCalculationError("Swiss Ephemeris could not calculate this chart.") from exc

    ascendant = houses["ascendant"]
    ascendant["house"] = 1
    _attach_whole_sign_houses(planets, ascendant)
    vargas = _build_varga_charts(planets, ascendant)

    moon_data = next((planet for planet in planets if planet["name"] == "Moon"), None)
    if moon_data is None:
        raise AstrologyCalculationError("Moon longitude is required for Vimshottari dasha.")
    dasha_data = calculate_dasha(local_dt, moon_data["longitude"])

    return {
        "calculation": {
            "ayanamsha": AYANAMSHA_NAME,
            "ayanamsha_mode": swe.get_ayanamsa_name(AYANAMSHA_MODE),
            "ayanamsha_value": round(ayanamsha_value, 8),
            "zodiac": "sidereal",
            "house_system": "Whole Sign",
            "julian_day_ut": round(jd_ut, 8),
            "ephemeris": "Swiss Ephemeris via pyswisseph",
            "planet_flags": ["SWIEPH", "SIDEREAL", "SPEED"],
            "node": "True Node",
        },
        "birth": {
            "date": birth_date.isoformat(),
            "time": birth_time.strftime("%H:%M:%S"),
            "local_datetime": local_dt.isoformat(),
            "utc_datetime": utc_dt.isoformat(),
            "timezone": city.timezone,
            "city_query": city.query,
            "resolved_place": city.display_name,
            "latitude": city.latitude,
            "longitude": city.longitude,
        },
        "lagna": ascendant,
        "planets": planets,
        "houses": houses["houses"],
        "vargas": vargas,
        "dasha": dasha_data,
    }


def _planet_positions(jd_ut: float, flags: int, ayanamsha_value: float) -> list[dict[str, Any]]:
    positions: list[dict[str, Any]] = []

    for name, swe_id in PLANETS.items():
        if swe_id == swe.TRUE_NODE:
            values, _ = swe.calc_ut(jd_ut, swe_id, NODE_TROPICAL_FLAGS)
            longitude = (float(values[0]) - ayanamsha_value) % 360
        else:
            values, _ = swe.calc_ut(jd_ut, swe_id, flags)
            longitude = float(values[0]) % 360
        speed = float(values[3])
        positions.append(
            {
                "name": name,
                **_longitude_payload(longitude),
                "speed_deg_per_day": round(speed, 6),
                "is_retrograde": speed < 0,
            }
        )

    rahu_longitude = next(item["longitude"] for item in positions if item["name"] == "Rahu")
    ketu_longitude = (rahu_longitude + 180) % 360
    positions.append(
        {
            "name": "Ketu",
            **_longitude_payload(ketu_longitude),
            "speed_deg_per_day": None,
            "is_retrograde": True,
        }
    )

    return positions


def _house_cusps(jd_ut: float, latitude: float, longitude: float) -> dict[str, Any]:
    house_system = b"W"

    try:
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system, HOUSE_FLAGS)
    except TypeError:
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system)

    cusp_values = list(cusps)
    if len(cusp_values) == 13:
        cusp_values = cusp_values[1:]

    houses = [
        {
            "house": index + 1,
            **_longitude_payload(float(cusp) % 360),
        }
        for index, cusp in enumerate(cusp_values[:12])
    ]

    return {
        "ascendant": {
            "name": "Lagna",
            **_longitude_payload(float(ascmc[0]) % 360),
        },
        "houses": houses,
    }


def _longitude_payload(longitude: float) -> dict[str, Any]:
    longitude = longitude % 360
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    nakshatra_span = 360 / 27
    nakshatra_index = min(26, int(longitude // nakshatra_span))
    pada = int((longitude % nakshatra_span) // (nakshatra_span / 4)) + 1

    return {
        "longitude": round(longitude, 6),
        "longitude_dms": _format_dms(longitude),
        "rashi": RASHIS[sign_index],
        "degree_in_rashi": round(degree_in_sign, 6),
        "degree_in_rashi_dms": _format_dms(degree_in_sign),
        "nakshatra": NAKSHATRAS[nakshatra_index],
        "nakshatra_pada": pada,
    }


def _attach_whole_sign_houses(planets: list[dict[str, Any]], ascendant: dict[str, Any]) -> None:
    lagna_sign = _sign_index_from_rashi(ascendant["rashi"])
    for planet in planets:
        planet_sign = _sign_index_from_rashi(planet["rashi"])
        planet["house"] = _relative_house(planet_sign, lagna_sign)


def _build_varga_charts(planets: list[dict[str, Any]], ascendant: dict[str, Any]) -> dict[str, Any]:
    d1_lagna_sign = _sign_index_from_rashi(ascendant["rashi"])
    d9_lagna = _varga_position(ascendant["longitude"], "D9")
    d10_lagna = _varga_position(ascendant["longitude"], "D10")

    return {
        "D1": {
            "name": "Rashi",
            "lagna": _d1_varga_payload(ascendant, d1_lagna_sign),
            "planets": [_d1_varga_payload(planet, d1_lagna_sign) for planet in planets],
        },
        "D9": {
            "name": "Navamsha",
            "lagna": _varga_body_payload("Lagna", d9_lagna, d9_lagna["sign_index"]),
            "planets": [
                _varga_body_payload(
                    planet["name"],
                    _varga_position(planet["longitude"], "D9"),
                    d9_lagna["sign_index"],
                    planet.get("is_retrograde"),
                )
                for planet in planets
            ],
        },
        "D10": {
            "name": "Dashamsha",
            "lagna": _varga_body_payload("Lagna", d10_lagna, d10_lagna["sign_index"]),
            "planets": [
                _varga_body_payload(
                    planet["name"],
                    _varga_position(planet["longitude"], "D10"),
                    d10_lagna["sign_index"],
                    planet.get("is_retrograde"),
                )
                for planet in planets
            ],
        },
    }


def _d1_varga_payload(body: dict[str, Any], lagna_sign_index: int) -> dict[str, Any]:
    sign_index = _sign_index_from_rashi(body["rashi"])
    return {
        "name": body["name"],
        "rashi": body["rashi"],
        "degree_in_rashi": body["degree_in_rashi"],
        "degree_in_rashi_dms": body["degree_in_rashi_dms"],
        "house": _relative_house(sign_index, lagna_sign_index),
        "longitude": body["longitude"],
        "longitude_dms": body["longitude_dms"],
        "is_retrograde": body.get("is_retrograde"),
    }


def _varga_position(longitude: float, chart: str) -> dict[str, Any]:
    longitude = longitude % 360
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30

    if chart == "D9":
        part_size = 30 / 9
        part_index = min(8, int(degree_in_sign // part_size))
        start_sign = _navamsha_start_sign(sign_index)
        varga_sign = (start_sign + part_index) % 12
        degree_in_varga = (degree_in_sign - part_index * part_size) * 9
    elif chart == "D10":
        part_size = 30 / 10
        part_index = min(9, int(degree_in_sign // part_size))
        start_sign = _dashamsha_start_sign(sign_index)
        varga_sign = (start_sign + part_index) % 12
        degree_in_varga = (degree_in_sign - part_index * part_size) * 10
    else:
        raise ValueError(f"Unsupported varga chart: {chart}")

    varga_longitude = (varga_sign * 30 + degree_in_varga) % 360
    return {
        "sign_index": varga_sign,
        "rashi": RASHIS[varga_sign],
        "degree_in_rashi": round(degree_in_varga, 6),
        "degree_in_rashi_dms": _format_dms(degree_in_varga),
        "longitude": round(varga_longitude, 6),
        "longitude_dms": _format_dms(varga_longitude),
    }


def _varga_body_payload(
    name: str,
    varga_position: dict[str, Any],
    varga_lagna_sign_index: int,
    is_retrograde: bool | None = None,
) -> dict[str, Any]:
    payload = {
        "name": name,
        "rashi": varga_position["rashi"],
        "degree_in_rashi": varga_position["degree_in_rashi"],
        "degree_in_rashi_dms": varga_position["degree_in_rashi_dms"],
        "house": _relative_house(varga_position["sign_index"], varga_lagna_sign_index),
        "longitude": varga_position["longitude"],
        "longitude_dms": varga_position["longitude_dms"],
    }
    if is_retrograde is not None:
        payload["is_retrograde"] = is_retrograde
    return payload


def _navamsha_start_sign(sign_index: int) -> int:
    modality = sign_index % 3
    if modality == 0:
        return sign_index
    if modality == 1:
        return (sign_index + 8) % 12
    return (sign_index + 4) % 12


def _dashamsha_start_sign(sign_index: int) -> int:
    sign_number = sign_index + 1
    is_odd_sign = sign_number % 2 == 1
    if is_odd_sign:
        return sign_index
    return (sign_index + 8) % 12


def _relative_house(sign_index: int, lagna_sign_index: int) -> int:
    return ((sign_index - lagna_sign_index) % 12) + 1


def _sign_index_from_rashi(rashi: str) -> int:
    return RASHIS.index(rashi)


def _ayanamsha_value(jd_ut: float) -> float:
    _flags, ayanamsha = swe.get_ayanamsa_ex_ut(jd_ut, swe.FLG_SWIEPH)
    return float(ayanamsha)


def _format_dms(value: float) -> str:
    value = value % 360
    degrees = int(value)
    minutes_full = abs(value - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60)

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1

    return f"{degrees:02d}d{minutes:02d}m{seconds:02d}s"
