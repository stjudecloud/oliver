from . import reporting
from urllib.parse import urlparse


def duration_to_text(duration):
    parts = []
    attrs = ["years", "months", "days", "hours", "minutes", "remaining_seconds"]
    for attr in attrs:
        if hasattr(duration, attr):
            value = getattr(duration, attr)
            # hack to get the correct formatting out. Pendulum appears to inconsistently
            # name its methods: https://github.com/sdispater/pendulum/blob/master/pendulum/duration.py#L163
            if attr == "remaining_seconds":
                attr = "seconds"

            if value > 0:
                parts.append(f"{value} {attr}")

    return " ".join(parts)


def is_url(url_string: str) -> bool:
    return (
        urlparse(url_string).scheme == "http" or urlparse(url_string).scheme == "https"
    )
