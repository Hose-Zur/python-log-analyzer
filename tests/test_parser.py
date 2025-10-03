"""
Goal: unit-test the Apache Combined line parser.
Scope: happy / edge / error / policy cases with concise contracts.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from src.analyzer.parser import parse_line, MAX_LINE_LEN


# === UTIL ====================================================================

@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Path to test data directory (optional; used by two small smoke tests)."""
    return Path(__file__).resolve().parents[1] / "data"


def mk_line(
    remote_host="127.0.0.1",
    identd="-",
    user="-",
    ts="10/Oct/2000:13:55:36 -0700",
    method="GET",
    path="/apache_pb.gif",
    protocol="HTTP/1.0",
    status="200",
    size="2326",
    referrer="http://www.example.com/start.html",
    user_agent='Mozilla/4.08 [en] (Win98; I ;Nav)',
):
    """Build a synthetic Combined line. Order: "request" status size "ref" "ua"."""
    req = f"{method} {path} {protocol}".strip()
    return (
        f"{remote_host} {identd} {user} "
        f"[{ts}] "
        f'"{req}" '
        f"{status} {size} "
        f'"{referrer}" '
        f'"{user_agent}"'
    )


# === HAPPY ===================================================================

def test_happy_basic_get_line_returns_dict_utc_ts():
    """Happy: valid line → dict with normalized UTC timestamp and fields set."""
    line = mk_line(
        remote_host="192.168.0.1",
        identd="-",
        user="John",
        ts="10/Jan/1990:12:35:16 +0700",
        method="POST",
        path="/api/apache_pb.gif",
        protocol="HTTP/3.0",
        status="305",
        size="23260",
        referrer="https://www.cisco.com/api/example.html",
        user_agent='Mozilla/4.08 [en] (Win98; I ;Nav)',
    )
    out = parse_line(line, fail_policy="strict")
    assert isinstance(out, dict)
    assert out["identd"] is None
    assert out["user"] == "John"
    assert out["ts"] == datetime(1990, 1, 10, 5, 35, 16, tzinfo=timezone.utc)
    assert out["method"] == "POST"
    assert out["path"] == "/api/apache_pb.gif"
    assert out["protocol"] == "HTTP/3.0"
    assert out["status"] == 305
    assert out["size"] == 23260
    assert out["referrer"] == "https://www.cisco.com/api/example.html"
    assert out["user_agent"] == 'Mozilla/4.08 [en] (Win98; I ;Nav)'


def test_happy_post_without_protocol():
    """Happy: protocol omitted → parsed as None; UTC conversion still correct."""
    line = mk_line(
        ts="29/Feb/2000:05:34:32 -1200",
        method="POST",
        path="/index.html",
        protocol="",
        status="599",
        size="0",
        referrer="-",
        user_agent="-",
    )
    out = parse_line(line, fail_policy="strict")
    assert out["ts"] == datetime(2000, 2, 29, 17, 34, 32, tzinfo=timezone.utc)
    assert out["method"] == "POST"
    assert out["path"] == "/index.html"
    assert out["protocol"] is None
    assert out["status"] == 599
    assert out["size"] == 0
    assert out["referrer"] is None
    assert out["user_agent"] is None


def test_happy_get_http11_converts_to_utc():
    """Happy: GET + HTTP/1.1 with +0200 offset → UTC normalized."""
    line = mk_line(method="GET", protocol="HTTP/1.1", ts="01/Jan/2024:01:00:00 +0200")
    out = parse_line(line, fail_policy="strict")
    assert out["ts"] == datetime(2023, 12, 31, 23, 0, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "method_in",
    ["get", "pOsT", "hEaD", "OpTiOnS"],
    ids=["get", "pOsT", "hEaD", "OpTiOnS"],
)
def test_happy_mixed_casing_methods_normalized(method_in: str):
    """Happy: mixed-case methods are normalized to uppercase and whitelisted."""
    out = parse_line(mk_line(method=method_in), fail_policy="strict")
    assert out["method"] == method_in.upper()


def test_happy_from_access_small_first_line(data_dir: Path):
    """Happy: first line from access_small.log parses (smoke test)."""
    p = data_dir / "access_small.log"
    line = p.read_text(encoding="utf-8", errors="strict").splitlines()[0]
    out = parse_line(line, fail_policy="strict")
    assert isinstance(out, dict)


# === EDGE ====================================================================

@pytest.mark.parametrize("ip", ["0.0.0.0", "255.255.255.255"], ids=["min", "max"])
def test_edge_ip_lower_and_upper_bounds(ip: str):
    """Edge: IPv4 extremes are accepted; UTC timestamp still correct."""
    line = mk_line(remote_host=ip, ts="29/Feb/2004:23:59:59 +1400")
    out = parse_line(line, fail_policy="strict")
    assert out["remote_host"] == ip
    assert out["ts"] == datetime(2004, 2, 29, 9, 59, 59, tzinfo=timezone.utc)


def test_edge_size_dash_becomes_none():
    """Edge: size '-' is parsed as None."""
    out = parse_line(mk_line(size="-"), fail_policy="strict")
    assert out["size"] is None


@pytest.mark.parametrize(
    "weird_path",
    ["/a/b;c=1", "/q?a=1&b=two", "/%E2%9C%93/ok"],
    ids=["semicolon", "query", "utf8-encoded"],
)
def test_edge_unusual_paths(weird_path: str):
    """Edge: unusual but valid paths are preserved as-is."""
    out = parse_line(mk_line(path=weird_path), fail_policy="strict")
    assert out["path"] == weird_path


@pytest.mark.parametrize("status", [100, 599], ids=["lower-bound", "upper-bound"])
def test_edge_status_lower_and_upper_bounds(status: int):
    """Edge: status lower/upper bound values parse as ints."""
    out = parse_line(mk_line(status=str(status)), fail_policy="strict")
    assert out["status"] == status
    assert isinstance(out["status"], int)


# === ERROR ===================================================================

def test_error_from_corrupted_first_line_skip_returns_none_logs_warning(data_dir: Path, caplog):
    """Error+skip: first corrupted line → None and a warning is logged."""
    p = data_dir / "corrupted.log"
    line = p.read_text(encoding="utf-8", errors="strict").splitlines()[0]

    with caplog.at_level("WARNING"):
        out = parse_line(line, fail_policy="skip")

    assert out is None
    assert any("parse_line skipped" in rec.message for rec in caplog.records)


def test_error_protocol_bad_shape_due_to_regex():
    """Error: non-HTTP token after method+path causes bad shape (strict regex)."""
    line = mk_line(protocol="HTP/1.1")
    with pytest.raises(ValueError, match="line: bad shape"):
        parse_line(line, fail_policy="strict")


def test_error_status_999_strict_raises_valueerror():
    """Error: status above 599 is rejected with explicit validation error."""
    line = mk_line(status="999")
    with pytest.raises(ValueError, match="status: out of range"):
        parse_line(line, fail_policy="strict")


def test_error_status_600_strict_raises_valueerror():
    """Error: status 600 is rejected with explicit validation error."""
    with pytest.raises(ValueError, match="status: out of range"):
        parse_line(mk_line(status="600"), fail_policy="strict")


def test_error_status_99_strict_raises_valueerror():
    """Error: too-short status (2 digits) breaks overall shape."""
    line = mk_line(status="99")
    with pytest.raises(ValueError, match="line: bad shape"):
        parse_line(line, fail_policy="strict")


def test_error_bad_timestamp_hour_strict():
    """Error: hour=99 triggers 'ts: bad time component'."""
    bad = mk_line(ts="10/Oct/2000:99:00:00 +0000")
    with pytest.raises(ValueError, match="ts: bad time component"):
        parse_line(bad, fail_policy="strict")


def test_error_missing_quotes_skip_returns_none_logs_warning(caplog):
    """Error+skip: missing final quote → None and a warning is logged."""
    bad = mk_line(ts="10/Oct/2000:13:55:36 -0700")[:-1]  # drop last '"'
    with caplog.at_level("WARNING"):
        out = parse_line(bad, fail_policy="skip")
    assert out is None
    assert any("parse_line skipped" in rec.message for rec in caplog.records)


def test_error_ts_brackets_missing_skip_returns_none():
    """Error+skip: timestamp without brackets → None (regex no-match)."""
    bad = mk_line(ts="10/Oct/2000:13:55:36 -0700")
    bad = bad.replace("[10/Oct/2000:13:55:36 -0700]", "10/Oct/2000:13:55:36 -0700")
    out = parse_line(bad, fail_policy="skip")
    assert out is None


def test_error_line_exceeds_max_length_policy_strict():
    """Error: total line length > MAX_LINE_LEN raises 'line: too long'."""
    base = mk_line(ts="10/Oct/2000:13:55:36 +0000")
    extra = "A" * (MAX_LINE_LEN - len(base) + 1)
    too_long = base[:-1] + extra + '"'  # keep closing quote
    with pytest.raises(ValueError, match="line: too long"):
        parse_line(too_long, fail_policy="strict")


# === POLICY ==================================================================

@pytest.mark.parametrize(
    "bad_method",
    ["GETS", "POSTS", "PUTS", "DELETES", "HEADS", "OPTIONSS", "PATCHS", "CONNECTS", "TRACES"],
)
def test_error_whitelists(bad_method: str):
    """Policy(strict): non-whitelisted methods are rejected."""
    with pytest.raises(ValueError, match="method: not allowed"):
        parse_line(mk_line(method=bad_method), fail_policy="strict")


def test_policy_skip_does_not_raise():
    """Policy(skip): invalid method yields None instead of raising."""
    out = parse_line(mk_line(method="TF"), fail_policy="skip")
    assert out is None


def test_policy_strict_raises_valueerror():
    """Policy(strict): invalid method raises ValueError."""
    with pytest.raises(ValueError):
        parse_line(mk_line(method="TF"), fail_policy="strict")
