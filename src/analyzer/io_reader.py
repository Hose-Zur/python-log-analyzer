# === TESTY IO READER ===
# Cel: zgodność z kontraktem read_log_lines.
#
# WYMAGANIA:
# - Strumieniowość (nie testujemy pamięci, ale zakładamy iteracyjne API).
# - Kolejność linii zachowana.
# - Limit: None/0 -> całość, N -> N linii, N > len -> len.
# - Błędy: brak pliku -> FileNotFoundError, limit < 0 -> ValueError.
# - Kodowanie: jawne latin-1 działa; fallback z utf-8 -> latin-1 działa.
#
# TODO:
# [x] test_lines_are_in_same_order
# [x] test_limit_none_returns_all_lines
# [x] test_limit_zero_returns_all_lines
# [x] test_limit_one_returns_first_line
# [x] test_limit_two_returns_two_lines
# [x] test_limit_larger_than_file  # (unikaj stałej 13; policz dynam.)
# [x] test_empty_file (tmp_path)
# [x] test_file_not_found
# [x] test_negative_limit_is_error
# [x] test_explicit_encoding_latin1
# [x] test_encoding_fallback_utf8_to_latin1
# [ ] (opcjonalnie) test_permission_error (jeśli chcesz zasymulować)

from pathlib import Path
from typing import Optional, Iterator
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG) to ma ustawic cli

def read_log_lines(path: Path, encoding: str = "utf-8", limit: Optional[int]= None) -> Iterator[str]:
    """
    Generator do strumieniowego odczytu linii z pliku logu.

    Parametry:
    ----------
    path : Path
        Ścieżka do pliku logu do odczytu.
    encoding : str, opcjonalnie (domyślnie "utf-8")
        Kodowanie znaków używane przy otwieraniu pliku.
    limit : Optional[int], opcjonalnie
        Maksymalna liczba linii do odczytania. Jeśli None lub 0, odczytywane są wszystkie linie.

    Zwraca:
    --------
    Generator[str]
        Generator zwracający kolejne linie pliku jako stringi (bez znaków końca linii i białych znaków po prawej stronie).

    Wyjątki:
    --------
    FileNotFoundError
        Jeśli plik nie istnieje lub nie można go otworzyć.
    UnicodeDecodeError
        Jeśli podane kodowanie jest niepoprawne. Wtedy funkcja próbuje fallback na "latin-1".
        W przypadku błędu kodowania plik jest ponownie otwierany od początku w latin-1.

    Zachowanie:
    -----------
    - Odczytuje plik linię po linii, bez wczytywania całego pliku do pamięci.
    - W przypadku błędu kodowania próbuje ponownie z kodowaniem "latin-1".
    - Jeśli ustawiono limit, odczyt kończy po osiągnięciu tej liczby linii.
    - Loguje błędy (wymaga wcześniejszej konfiguracji loggera).
    """

    if not path.is_file():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(str(path))
    
    if limit is not None and limit < 0:
        raise ValueError(f"Parametr 'limit' musi być nieujemny, otrzymano: {limit}")

    try:
        with open(path, "r", encoding=encoding) as file:
            for count, line in enumerate(file, start=1):
                yield line.rstrip()
                if limit is not None and limit > 0 and count >= limit:
                    break
    
    except UnicodeDecodeError:
        logger.error("Błąd kodowania, ponowne otwarcie pliku z latin-1")
        count = 0
        with open(path, "r", encoding="latin-1") as file:
            for count, line in enumerate(file, start=1):
                yield line.rstrip()
                if limit is not None and limit > 0 and count >= limit:
                    break
    
    except PermissionError as e:
        logger.error(f"Brak uprawnień do pliku: {path} ({e})")
        raise PermissionError(f"Brak uprawnień do pliku: {path}") from e
    
    except OSError as e:
        logger.error(f"Błąd systemowy podczas otwierania pliku: {path} ({e})")
        raise OSError(f"Błąd systemowy podczas otwierania pliku: {path}") from e