"""Vimshottari dasha calculation from the Moon's exact sidereal longitude."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

VIMSHOTTARI_YEAR_DAYS = 365.25
TOTAL_DASHA_YEARS = 120
NAKSHATRA_SPAN_DEGREES = 360 / 27

MAHA_DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
MAHA_DASHA_DURATION = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

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


def calculate_dasha(
    birth_datetime: datetime,
    moon_longitude: float,
    years_to_generate: int = 120,
    current_datetime: datetime | None = None,
) -> dict[str, Any]:
    moon_longitude = moon_longitude % 360
    nakshatra_index = min(26, int(moon_longitude // NAKSHATRA_SPAN_DEGREES))
    nakshatra_name = NAKSHATRAS[nakshatra_index]
    lord = MAHA_DASHA_ORDER[nakshatra_index % len(MAHA_DASHA_ORDER)]
    lord_index = MAHA_DASHA_ORDER.index(lord)

    degrees_elapsed = moon_longitude - nakshatra_index * NAKSHATRA_SPAN_DEGREES
    fraction_elapsed = degrees_elapsed / NAKSHATRA_SPAN_DEGREES
    fraction_remaining = 1 - fraction_elapsed

    lord_duration_days = _duration_days(lord)
    elapsed_days = lord_duration_days * fraction_elapsed
    balance_days = lord_duration_days * fraction_remaining
    first_maha_start = birth_datetime - timedelta(days=elapsed_days)
    first_maha_end = birth_datetime + timedelta(days=balance_days)

    maha_dashas = _build_maha_dashas(
        first_lord_index=lord_index,
        first_start=first_maha_start,
        years_to_generate=years_to_generate,
    )
    now = current_datetime or datetime.now(tz=birth_datetime.tzinfo)
    current_maha = _find_period(maha_dashas, now) or maha_dashas[-1]
    current_antara = _find_period(current_maha["antara_dashas"], now)
    next_maha = _next_period(maha_dashas, current_maha)

    return {
        "system": "Vimshottari",
        "year_length_days": VIMSHOTTARI_YEAR_DAYS,
        "birth_nakshatra": {
            "name": nakshatra_name,
            "lord": lord,
            "moon_longitude": round(moon_longitude, 6),
            "degrees_elapsed_in_nakshatra": round(degrees_elapsed, 6),
            "degrees_remaining_in_nakshatra": round(NAKSHATRA_SPAN_DEGREES - degrees_elapsed, 6),
            "fraction_elapsed": round(fraction_elapsed, 10),
            "fraction_remaining": round(fraction_remaining, 10),
        },
        "balance_at_birth": {
            "maha_dasha_lord": lord,
            "balance_days": round(balance_days, 6),
            "balance_years": round(balance_days / VIMSHOTTARI_YEAR_DAYS, 8),
            "maha_dasha_start": _date_str(first_maha_start),
            "maha_dasha_end": _date_str(first_maha_end),
        },
        "current_maha_dasha": _current_payload(current_maha, now),
        "current_antara_dasha": _current_payload(current_antara, now) if current_antara else None,
        "next_maha_dasha": _basic_period_payload(next_maha) if next_maha else None,
        "antara_dashas": current_maha["antara_dashas"],
        "maha_dashas": maha_dashas,
        "upcoming_maha_dashas": [_basic_period_payload(period) for period in _upcoming_periods(maha_dashas, now, count=5)],
    }


def _build_maha_dashas(first_lord_index: int, first_start: datetime, years_to_generate: int) -> list[dict[str, Any]]:
    dashas: list[dict[str, Any]] = []
    start = first_start
    index = first_lord_index
    generated_days = 0.0
    target_days = years_to_generate * VIMSHOTTARI_YEAR_DAYS

    while generated_days < target_days + max(MAHA_DASHA_DURATION.values()) * VIMSHOTTARI_YEAR_DAYS:
        lord = MAHA_DASHA_ORDER[index % len(MAHA_DASHA_ORDER)]
        duration_days = _duration_days(lord)
        end = start + timedelta(days=duration_days)
        dashas.append(
            {
                "planet": lord,
                "start_date": _date_str(start),
                "end_date": _date_str(end),
                "start_datetime": start.isoformat(),
                "end_datetime": end.isoformat(),
                "duration_years": MAHA_DASHA_DURATION[lord],
                "duration_days": round(duration_days, 6),
                "antara_dashas": _build_antara_dashas(lord, start, end),
            }
        )
        generated_days += duration_days
        start = end
        index += 1

    return dashas


def _build_antara_dashas(maha_lord: str, maha_start: datetime, maha_end: datetime) -> list[dict[str, Any]]:
    antar_dashas: list[dict[str, Any]] = []
    maha_duration_days = (maha_end - maha_start).total_seconds() / 86400
    start = maha_start
    start_index = MAHA_DASHA_ORDER.index(maha_lord)

    for offset in range(len(MAHA_DASHA_ORDER)):
        lord = MAHA_DASHA_ORDER[(start_index + offset) % len(MAHA_DASHA_ORDER)]
        duration_days = maha_duration_days * MAHA_DASHA_DURATION[lord] / TOTAL_DASHA_YEARS
        end = start + timedelta(days=duration_days)
        antar_dashas.append(
            {
                "planet": lord,
                "start_date": _date_str(start),
                "end_date": _date_str(end),
                "start_datetime": start.isoformat(),
                "end_datetime": end.isoformat(),
                "duration_days": round(duration_days, 6),
                "duration_months": round(duration_days * 12 / VIMSHOTTARI_YEAR_DAYS, 3),
                "is_current": False,
                "remaining_days": None,
            }
        )
        start = end

    return antar_dashas


def _find_period(periods: list[dict[str, Any]], moment: datetime) -> dict[str, Any] | None:
    for period in periods:
        start = datetime.fromisoformat(period["start_datetime"])
        end = datetime.fromisoformat(period["end_datetime"])
        if start <= moment < end:
            return period
    return None


def _next_period(periods: list[dict[str, Any]], current: dict[str, Any]) -> dict[str, Any] | None:
    try:
        index = periods.index(current)
    except ValueError:
        return None
    if index + 1 >= len(periods):
        return None
    return periods[index + 1]


def _upcoming_periods(periods: list[dict[str, Any]], moment: datetime, count: int) -> list[dict[str, Any]]:
    upcoming = []
    for period in periods:
        if datetime.fromisoformat(period["start_datetime"]) >= moment:
            upcoming.append(period)
        if len(upcoming) == count:
            break
    return upcoming


def _current_payload(period: dict[str, Any], now: datetime) -> dict[str, Any]:
    payload = _basic_period_payload(period)
    end = datetime.fromisoformat(period["end_datetime"])
    payload["remaining_days"] = max(0, int((end - now).total_seconds() // 86400))
    if "antara_dashas" in period:
        marked_antaras = []
        for antara in period["antara_dashas"]:
            copy = dict(antara)
            start = datetime.fromisoformat(copy["start_datetime"])
            antara_end = datetime.fromisoformat(copy["end_datetime"])
            copy["is_current"] = start <= now < antara_end
            copy["remaining_days"] = (
                max(0, int((antara_end - now).total_seconds() // 86400)) if copy["is_current"] else None
            )
            marked_antaras.append(copy)
        period["antara_dashas"] = marked_antaras
    return payload


def _basic_period_payload(period: dict[str, Any]) -> dict[str, Any]:
    return {
        "planet": period["planet"],
        "start_date": period["start_date"],
        "end_date": period["end_date"],
        "duration_years": period.get("duration_years"),
        "duration_days": period.get("duration_days"),
    }


def _duration_days(planet: str) -> float:
    return MAHA_DASHA_DURATION[planet] * VIMSHOTTARI_YEAR_DAYS


def _date_str(value: datetime) -> str:
    return value.date().isoformat()
