# tests/test_io_reader.py
import pytest
from pathlib import Path
from src.analyzer.io_reader import read_log_lines


def test_lines_are_in_same_order():
    """Sprawdza, że linie zwrócone przez read_log_lines są w tej samej kolejności co w pliku."""
    path = Path("data/access_big.log")
    with path.open(encoding="utf-8") as f:
        expected_lines = f.read().splitlines()
    lines = list(read_log_lines(path))
    assert lines == expected_lines


def test_limit_none_returns_all_lines():
    """Sprawdza, że limit=None zwraca wszystkie linie."""
    path = Path("data/access_big.log")
    lines = list(read_log_lines(path, limit=None))
    with path.open(encoding="utf-8") as f:
        expected_count = sum(1 for _ in f)
    assert len(lines) == expected_count


def test_limit_zero_returns_all_lines():
    """Sprawdza, że limit=0 zwraca wszystkie linie (tak jak None)."""
    path = Path("data/access_big.log")
    lines = list(read_log_lines(path, limit=0))
    with path.open(encoding="utf-8") as f:
        expected_count = sum(1 for _ in f)
    assert len(lines) == expected_count


def test_limit_one_returns_first_line():
    """Sprawdza, że limit=1 zwraca tylko jedną linię."""
    path = Path("data/access_small.log")
    lines = list(read_log_lines(path, limit=1))
    assert len(lines) == 1


def test_limit_two_returns_two_lines():
    """Sprawdza, że limit=2 zwraca dokładnie dwie linie."""
    path = Path("data/access_small.log")
    lines = list(read_log_lines(path, limit=2))
    assert len(lines) == 2


def test_limit_larger_than_file():
    """Sprawdza, że limit większy niż liczba linii zwraca wszystkie linie."""
    path = Path("data/access_small.log")
    lines = list(read_log_lines(path, limit=1000))
    assert len(lines) == 13


def test_empty_file(tmp_path):
    """Sprawdza, że pusty plik zwraca pustą listę linii."""
    empty_file = tmp_path / "empty.log"
    empty_file.write_text("", encoding="utf-8")
    lines = list(read_log_lines(empty_file))
    assert lines == []


def test_file_not_found():
    """Sprawdza, że brak pliku rzuca FileNotFoundError."""
    path = Path("data/__no_such__.log")
    with pytest.raises(FileNotFoundError):
        _ = list(read_log_lines(path))


def test_negative_limit_is_error():
    """Sprawdza, że limit < 0 rzuca ValueError."""
    path = Path("data/access_small.log")
    with pytest.raises(ValueError):
        _ = list(read_log_lines(path, limit=-1))


def test_explicit_encoding_latin1(tmp_path):
    """Sprawdza odczyt pliku Latin-1 z jawnie podanym kodowaniem."""
    file_path = tmp_path / "latin1_file.log"
    content = b'Simple line\ncaf\xe9 test\n\xa3100 price\n'
    file_path.write_bytes(content)

    lines = list(read_log_lines(file_path, encoding="latin-1"))
    assert len(lines) == 3
    assert "Simple line" == lines[0]
    assert "café test" == lines[1]
    assert "£100 price" == lines[2]


def test_encoding_fallback_utf8_to_latin1(tmp_path):
    """Sprawdza fallback: plik z błędnym UTF-8 odczytywany jest w latin-1."""
    file_path = tmp_path / "corrupted_utf8.log"
    content = b'Simple line\n\x80\x81\x82 bad utf8\nEnd line\n'
    file_path.write_bytes(content)

    lines = list(read_log_lines(file_path, encoding="utf-8"))
    assert len(lines) == 3
    assert "Simple line" == lines[0]
    assert "End line" == lines[2]
