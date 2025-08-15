# === TESTY IO READER (tests/test_io_reader.py) ===
# Cel: sprawdzić, że read_log_lines działa strumieniowo, obsługuje limit i błędy.

# TODO:
# [ ] zaimportuj Path oraz funkcję read_log_lines z analyzer.io_reader
# [ ] użyj małych plików z katalogu data/ (access_small.log, corrupted.log)
# [ ] test: plik istnieje -> liczy poprawnie linie
# [ ] test: limit=2 -> zwraca dokładnie 2 linie
# [ ] test: plik nie istnieje -> FileNotFoundError
# [ ] (opcjonalnie) złe kodowanie -> UnicodeDecodeError (lub fallback w Twojej implementacji)
# [ ] NIE wczytuj całego pliku do pamięci

import pytest
from pathlib import Path
from src.analyzer.io_reader import read_log_lines


def test_read_all_lines_counts_ok():
    path = Path("data/access_big.log")
    lines = list(read_log_lines(path))
    assert len(lines) >= 5512
    # (opcjonalnie) porównaj z rzeczywistą liczbą linii z pliku

def test_limit_two_lines():
    path = Path("data/access_small.log")
    lines = list(read_log_lines(path, limit=2))
    assert len(lines) == 2

def test_file_not_found():
    path = Path("data/__no_such__.log")
    with pytest.raises(FileNotFoundError):
        _ = list(read_log_lines(path))

def test_negative_limit_is_error():
    path = Path("data/access_small.log")
    with pytest.raises(ValueError):
        _ = list(read_log_lines(path, limit=-1))
