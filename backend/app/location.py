from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


class CityLookupError(ValueError):
    pass


@dataclass(frozen=True)
class GeocodedCity:
    query: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str


_TIMEZONE_FINDER = TimezoneFinder()


def geocode_city(city_name: str, user_agent: str, geocoder: Any | None = None, country_codes: str | None = None) -> GeocodedCity:
    query = city_name.strip()
    if len(query) < 2:
        raise CityLookupError("Enter a valid city name.")

    locator = geocoder or Nominatim(user_agent=user_agent, timeout=10)

    kwargs = {
        "exactly_one": True,
        "addressdetails": True,
    }
    if country_codes:
        kwargs["country_codes"] = country_codes

    try:
        location = locator.geocode(query, **kwargs)
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        raise CityLookupError(f"Could not geocode '{query}'. Try again in a moment.") from exc

    if location is None:
        raise CityLookupError(f"Could not find coordinates for '{query}'.")

    latitude = float(location.latitude)
    longitude = float(location.longitude)
    timezone_name = resolve_timezone(latitude, longitude)

    return GeocodedCity(
        query=query,
        display_name=getattr(location, "address", query),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )


def resolve_timezone(latitude: float, longitude: float) -> str:
    return (
        _TIMEZONE_FINDER.timezone_at(lat=latitude, lng=longitude)
        or _TIMEZONE_FINDER.closest_timezone_at(lat=latitude, lng=longitude)
        or "UTC"
    )
