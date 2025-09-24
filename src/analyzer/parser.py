"""
Module: parser.py
Cel: Parsowanie linii logów HTTP w formacie Apache Combined do słownika (normalized, tz-aware).
Public API:
  - def parse_line(line: str, fail_policy: str = "skip") -> dict | None
      Wejście: surowa linia; Wyjście: dict z polami:
        {
          "remote_host": str,            # IPv4 zwalidowane (0–255 w oktetach)
          "identd": str | None,          # '-' → None
          "user": str | None,            # '-' → None
          "ts": datetime,                # tz-aware, znormalizowany do UTC
          "method": str,                 # whitelist metod
          "path": str,                   # niepusta ścieżka/url (bez spacji)
          "protocol": str | None,        # 'HTTP/x.y' lub None (gdy brak)
          "status": int,                 # 100–599
          "size": int | None,            # '-' → None
          "referrer": str | None,        # '-' → None
          "user_agent": str | None       # '-' → None
        }
      Polityka błędów:
        - "skip": zwróć None i zaloguj ostrzeżenie na loggerze modułu,
        - "strict": podnieś ValueError z krótką diagnozą.
Wyjątki:
  - ValueError przy "strict" (zła składnia, zły status/metoda/IP, zła data, linia > limit).
Bezpieczeństwo:
  - Limit długości linii (domyśl: 16 MiB) – odrzuca nadmiernie długie rekordy.
  - Brak eval/exec, brak parsowania niekontrolowanych fragmentów jako kodu.
  - Walidacje pól liczbowych, zakresów i formatu IP; świadome logowanie (bez PII).
TODO (lekcja 3):
  [x] PRECOMPILED_COMBINED_RE: regex z nazwanymi grupami (remote_host, identd, user, ts, method, path, protocol, status, size, referrer, user_agent)
  [x] WHITELIST_METHODS: {"GET","POST","PUT","DELETE","HEAD","OPTIONS","PATCH","CONNECT","TRACE"}
  [ ] parse_request(raw: str) -> tuple[str, str, str | None]
  [x] parse_timestamp(raw: str) -> datetime     # tz-aware i normalizacja do UTC
  [x] is_ipv4(text: str) -> bool                # format + zakres 0–255
  [x] parse_size(text: str) -> int | None       # '-' → None
  [x] parse_line(line: str, fail_policy: str = "skip") -> dict | None
"""
# imports: stdlib -> third-party -> local
from __future__ import annotations

import re, logging
from datetime import datetime, timezone, timedelta
from typing import Final

logger = logging.getLogger(__name__)

MAX_LINE_LEN: Final[int] = 16 * 1024 * 1024  # 16MiB

PRECOMPILED_COMBINED_RE = re.compile(
    r"""
    ^                                              # start of line

    # IPv4 (0.0.0.0–255.255.255.255)
    (?P<remote_host>
        (?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)
        (?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}
    )
    \s+                                            # separator

    # identd and user (often "-")
    (?P<identd>\S+)
    \s+
    (?P<user>\S+)
    \s+

    # timestamp in square brackets
    \[
        (?P<ts>[^\]]+)
    \]
    \s+

    # request line: "METHOD SP PATH [SP PROTOCOL]" (protocol optional)
    "
        (?P<method>[A-Z]+)
        \s+
        (?P<path>\S+)
        (?:\s+(?P<protocol>HTTP/\d(?:\.\d)?))?
    "
    \s+

    # status and response size
    (?P<status>\d{3})
    \s+
    (?P<size>(?:\d+|-))
    \s+

    # referrer and user-agent (allow escaped quotes)
    "
        (?P<referrer>(?:[^"\\]|\\.)*)
    "
    \s+
    "
        (?P<user_agent>(?:[^"\\]|\\.)*)
    "

    $                                              # end of line
    """,
    re.VERBOSE,
)


# Three-letter English month abbreviations (canonical, upper-case)
MONTHS_ABBR: Final[tuple[str, ...]] = (
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
)

# Map month abbreviation -> 1..12 (used by parse_timestamp)
MONTH_INDEX: Final[dict[str, int]] = {abbr: i for i, abbr in enumerate(MONTHS_ABBR, start=1)}

# Strict Apache-style timestamp shape: exactly one ASCII space before the offset.
TS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<day>\d{2})/(?P<mon>[A-Za-z]{3})/(?P<year>\d{4})"
    r":(?P<hh>\d{2}):(?P<mm>\d{2}):(?P<ss>\d{2}) "
    r"(?P<sign>[+-])(?P<offhh>\d{2})(?P<offmm>\d{2})$"
)

# Allowed HTTP methods (immutable)
ALLOWED_HTTP_METHODS: Final[frozenset[str]] = frozenset({
    "GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH", "CONNECT", "TRACE",
})


# Protocol validator: HTTP/1.0, HTTP/1.1, HTTP/2, HTTP/3
PROTO_RE: Final[re.Pattern[str]] = re.compile(r"HTTP/\d(?:\.\d)?")

def is_ipv4(text: str) -> bool:
    """
    Return True iff `text` is a canonical IPv4 address.

    Rules:
      - Exactly four dot-separated decimal octets.
      - Each octet uses ASCII digits only and is in 0..255.
      - No leading zeros for multi-digit octets (e.g., '01' is invalid).
      - Surrounding whitespace is ignored; internal whitespace is not allowed.

    This is a pure validator and never raises exceptions.
    """
    s = text.strip()
    octets = s.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        # ASCII digits only (no unicode digits)
        if not (octet and octet.isascii() and octet.isdecimal()):
            return False

        # Disallow leading zeros in multi-digit octets (e.g., '01', '001')
        if len(octet) > 1 and octet[0] == "0":
            return False

        value = int(octet)
        if not (0 <= value <= 255):
            return False

    return True

def parse_size(text: str) -> int | None:
    """
    Parse HTTP response size field.

    Rules:
      - "-" or "" => None (no size reported).
      - Otherwise: ASCII decimal integer >= 0.
      - Leading zeros are allowed and normalized (e.g., "0005" -> 5).
    Raises:
      ValueError: if the input contains non-digits, signs, internal spaces, or other invalid characters.
    """
    s = text.strip()
    if s in ("", "-"):
        return None

    # ASCII digits only; disallows "+", "-", spaces, commas, etc.
    if not (s.isascii() and s.isdecimal()):
        raise ValueError("size must be ASCII decimal digits")

    value = int(s)  # normalizes leading zeros
    # isdecimal() guarantees non-negative, but keep the check for clarity/future changes
    if value < 0:
        raise ValueError("size cannot be negative")

    return value


def parse_timestamp(raw: str) -> datetime:
    """
    Parse Apache-style timestamp (inside the square brackets) into a UTC-aware datetime.

    Expected input shape (strict):
        "DD/Mon/YYYY:HH:MM:SS ±HHMM"
        e.g. "10/Oct/2023:13:55:36 +0200"

    Behavior:
      - Validates shape, month token, time ranges, and timezone offset ranges.
      - Builds a fixed-offset local datetime and converts it to UTC.
      - Returns tz-aware datetime in UTC.

    Raises:
      ValueError:
        - "ts: bad timestamp format"  -> shape mismatch
        - "ts: bad month token"       -> month not in {Jan..Dec}
        - "ts: bad time component"    -> HH∉[0,23] or MM/SS∉[0,59]
        - "ts: bad tz offset"         -> offset HH∉[0,14] or MM∉[0,59]
        - "ts: invalid calendar date" -> impossible date (e.g., 31/Feb)

    Examples:
      >>> parse_timestamp("10/Oct/2023:13:55:36 +0200")
      datetime.datetime(2023, 10, 10, 11, 55, 36, tzinfo=datetime.timezone.utc)
    """
    s = raw.strip()

    m = TS_RE.fullmatch(s)
    if not m:
        raise ValueError("ts: bad timestamp format")

    gd = m.groupdict()

    mon_tok = gd["mon"].upper()
    if mon_tok not in MONTH_INDEX:
        raise ValueError("ts: bad month token")
    month = MONTH_INDEX[mon_tok]

    day: int = int(gd["day"])
    year: int = int(gd["year"])
    hour: int = int(gd["hh"])
    minutes: int = int(gd["mm"])
    seconds: int = int(gd["ss"])

    if not (0 <= hour <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
        raise ValueError("ts: bad time component")

    off_h: int = int(gd["offhh"])
    off_m: int = int(gd["offmm"])
    if not (0 <= off_h <= 14 and 0 <= off_m <= 59):
        raise ValueError("ts: bad tz offset")

    offset_minutes = off_h * 60 + off_m
    if gd["sign"] == "-":
        offset_minutes = -offset_minutes

    tz = timezone(timedelta(minutes=offset_minutes))
    try:
        local_dt = datetime(year, month, day, hour, minutes, seconds, tzinfo=tz)
    except ValueError as _:
        # e.g. 31/Feb, 29/Feb in a non-leap year
        raise ValueError("ts: invalid calendar date") from None

    return local_dt.astimezone(timezone.utc)

def parse_line(line: str, fail_policy: str = "skip") -> dict | None:
    """
    Parse a single Apache Combined log line into a normalized dict.

    Parameters
    ----------
    line : str
        Raw log line (may include a trailing newline).
    fail_policy : {"skip", "strict"}
        - "skip": return None and log a warning on invalid input.
        - "strict": raise ValueError with a short diagnostic message.

    Returns
    -------
    dict | None
        On success, a dictionary with fields:
        {
          "remote_host": str,          # validated IPv4 (0..255 per octet)
          "identd": str | None,        # "-" -> None
          "user": str | None,          # "-" -> None
          "ts": datetime,              # tz-aware UTC datetime
          "method": str,               # allowed HTTP method
          "path": str,                 # non-empty, no spaces
          "protocol": str | None,      # "HTTP/x.y" or "HTTP/2"/"HTTP/3" or None
          "status": int,               # 100..599
          "size": int | None,          # "-" -> None
          "referrer": str | None,      # "-" -> None (escaped quotes de-escaped)
          "user_agent": str | None     # "-" -> None (escaped quotes de-escaped)
        }
        Returns None when fail_policy="skip" and the line is invalid.

    Raises
    ------
    ValueError
        Only when fail_policy="strict".
    """
    try:
        # Basic DOS guard
        if len(line) > MAX_LINE_LEN:
            raise ValueError("line: too long")

        # Keep leading spaces intact; drop only line endings
        text = line.rstrip("\r\n")

        match = PRECOMPILED_COMBINED_RE.fullmatch(text)
        if not match:
            raise ValueError("line: bad shape")

        groups = match.groupdict()

        # Remote host
        remote_host = groups["remote_host"]
        # NOTE: Combined regex already enforces canonical IPv4. If you plan to
        #       support hostnames/IPv6 later, relax the regex and validate here.

        # Identifiers ("-" -> None)
        identd = None if groups["identd"] == "-" else groups["identd"]
        user = None if groups["user"] == "-" else groups["user"]

        # Timestamp (tz-aware UTC)
        timestamp = parse_timestamp(groups["ts"])

        # Request-line fields
        method = groups["method"]  # regex enforces [A-Z]+
        if method not in ALLOWED_HTTP_METHODS:
            raise ValueError("method: not allowed")

        path = groups["path"]
        if not path or " " in path:
            raise ValueError("path: invalid")

        protocol = groups["protocol"]
        if protocol is not None and not PROTO_RE.fullmatch(protocol):
            raise ValueError("protocol: invalid")

        # Status code
        status = int(groups["status"])
        if not (100 <= status <= 599):
            raise ValueError("status: out of range")

        # Size
        try:
            size = parse_size(groups["size"])  # int | None
        except ValueError:
            raise ValueError("size: invalid")

        # Referrer / User-Agent ("-" -> None), de-escape \" -> "
        referrer = None if groups["referrer"] == "-" else groups["referrer"].replace(r'\"', '"')
        user_agent = None if groups["user_agent"] == "-" else groups["user_agent"].replace(r'\"', '"')

        return {
            "remote_host": remote_host,
            "identd": identd,
            "user": user,
            "ts": timestamp,
            "method": method,
            "path": path,
            "protocol": protocol,
            "status": status,
            "size": size,
            "referrer": referrer,
            "user_agent": user_agent,
        }

    except ValueError as exc:
        if fail_policy == "strict":
            raise
        logger.warning(f"parse_line skipped: {exc}")
        return None
