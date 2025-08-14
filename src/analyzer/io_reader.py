# === IO READER ===
# Cel: strumieniowo czytać pliki logów linia po linii, z obsługą błędów i limitem.
#
# ✅ Wymagania:
# - Wejście: ścieżka do pliku (Path), encoding (str), limit (Optional[int]).
# - Sprawdź, czy plik istnieje i jest plikiem.
# - Otwórz plik z danym encodingiem.
# - Iteruj po liniach bez wczytywania całego pliku do pamięci.
# - Jeśli limit > 0, zakończ po odczytaniu limitu linii.
# - Rzucaj sensowne wyjątki przy problemach (np. FileNotFoundError).
#
# 🔒 Bezpieczeństwo / odporność:
# - Nie zakładaj poprawnego kodowania — obsłuż UnicodeDecodeError (zaplanuj strategię).
# - Dodaj krótkie logowanie błędów (później wpięte do loggera).
#
# 📌 Interfejs publiczny (do zrobienia):
# - funkcja: read_log_lines(path: Path, encoding: str = "utf-8", limit: Optional[int] = None)
#   - Zwraca iterator/generator linii.
#
# 🧪 Testy (patrz tests/test_io_reader.py):
# - Gdy plik istnieje → zwraca poprawną liczbę linii.
# - Gdy limit ustawiony → zwraca dokładnie `limit` linii.
# - Gdy plik nie istnieje → odpowiedni wyjątek.
# - Gdy błędne kodowanie → zdefiniowana reakcja (np. wyjątek lub fallback).
#
# TODO:
# [ ] zaimportuj potrzebne rzeczy (pathlib.Path, typing.Optional)
# [ ] zdefiniuj sygnaturę funkcji read_log_lines(...)
# [ ] sprawdź istnienie pliku i poprawny typ (is_file)
# [ ] otwórz plik w try/catch, obsłuż UnicodeDecodeError
# [ ] iteruj po liniach (for ...), yield każdą linię
# [ ] jeśli limit -> przerwij po N liniach
# [ ] dodaj minimalne docstringi (opis parametrów i wyjątków)
# [ ] (opcjonalnie) policz liczbę linii i zwróć w metadanych — na razie NIE, tylko linie
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