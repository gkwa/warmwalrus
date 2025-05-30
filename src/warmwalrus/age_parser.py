import re
import typing


class AgeParser:
    """Parses age specifications like '10m', '1d', '2.3w'."""

    TIME_UNITS: typing.Dict[str, int] = {
        "s": 1,  # seconds
        "m": 60,  # minutes
        "h": 3600,  # hours
        "d": 86400,  # days
        "w": 604800,  # weeks
    }

    def parse_age(self, age_str: str) -> float:
        """Parse age string and return seconds."""
        pattern: str = r"^(\d+(?:\.\d+)?)([smhdw])$"
        match: typing.Optional[typing.Match[str]] = re.match(pattern, age_str.lower())

        if not match:
            raise ValueError(f"Invalid age format: {age_str}")

        value: str
        unit: str
        value, unit = match.groups()
        multiplier: typing.Optional[int] = self.TIME_UNITS.get(unit)

        if multiplier is None:
            raise ValueError(f"Unknown time unit: {unit}")

        return float(value) * multiplier
