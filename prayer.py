import datetime
import requests

PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

REQUEST_TIMEOUT = 10  # seconds


def _fetch_timings(url, params):
    """
    Internal helper. Calls the Aladhan API and returns a tuple of the five
    prayer times in PRAYERS order. Raises requests.RequestException on
    network/HTTP failures so callers can decide how to handle them.
    """
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    timings = response.json()["data"]["timings"]
    return tuple(timings[p] for p in PRAYERS)


def _tomorrow_str():
    return (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")


def get_prayer_times(city, country, method=2):
    return _fetch_timings(
        "https://api.aladhan.com/v1/timingsByCity",
        {"city": city, "country": country, "method": method},
    )


def get_tomorrow_prayer_times(city, country, method=2):
    return _fetch_timings(
        "https://api.aladhan.com/v1/timingsByCity",
        {
            "city": city,
            "country": country,
            "method": method,
            "date": _tomorrow_str(),
        },
    )


def get_prayer_times_lat(lat, lon, method=2):
    return _fetch_timings(
        "https://api.aladhan.com/v1/timings",
        {"latitude": lat, "longitude": lon, "method": method},
    )


def get_tomorrow_prayer_times_lat(lat, lon, method=2):
    return _fetch_timings(
        "https://api.aladhan.com/v1/timings",
        {
            "latitude": lat,
            "longitude": lon,
            "method": method,
            "date": _tomorrow_str(),
        },
    )


# Backwards-compatible alias for the old misspelled name, in case
# anything still imports it. New code should use the corrected name.
get_tomrrow_prayer_times = get_tomorrow_prayer_times