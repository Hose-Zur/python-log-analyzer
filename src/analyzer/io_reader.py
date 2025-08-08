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
