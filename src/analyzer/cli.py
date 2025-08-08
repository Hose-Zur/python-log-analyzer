# === CLI ===
# Cel: pobrać argumenty od użytkownika i uruchomić „pipeline”:
# Reader -> (Parser -> Aggregator -> Reporter) — na razie tylko Reader.
#
# ✅ Wymagania z README (Specyfikacja CLI):
# --input (wymagane, ścieżka)
# --outdir (domyślnie ./reports)
# --format (txt|csv|json; domyślnie txt)
# --top (int; domyślnie 10)
# --time-bucket (hour|day; domyślnie hour)
# --limit (int; opcjonalnie)
# --fail-policy (skip|strict; domyślnie skip)  # użyjesz w parserze
# --encoding (domyślnie utf-8)
# --quiet (flaga)
# --version (flaga)
#
# 🧩 Na tym etapie (Lekcja 2):
# - Użyj tylko: --input, --encoding, --limit (reszta placeholdery).
# - Po odczycie kilku linii wypisz podsumowanie (np. liczbę wczytanych linii)
#   albo po prostu policz je w zmiennej — NA RAZIE BEZ PARSOWANIA.
#
# 💡 Implementacyjnie sugeruję Typer (łatwiejszy niż argparse),
#    ale jeśli nie chcesz go jeszcze używać — zrób placeholdery (komentarze).
#
# 🧪 Testy CLI (smoke) w tests/test_cli.py:
# - uruchom CLI z poprawnym plikiem → proces wychodzi statusem 0
# - uruchom z nieistniejącym plikiem → ≠ 0, krótki komunikat błędu
#
# TODO:
# [ ] zaimportuj Typer (jeśli używasz) i Path (pathlib)
# [ ] stwórz aplikację CLI (np. app = Typer()) — placeholder
# [ ] zdefiniuj komendę główną i argumenty (input, encoding, limit) — placeholder
# [ ] wewnątrz komendy: wywołaj read_log_lines(...) i policz N pierwszych linii
# [ ] jeśli plik nie istnieje → zakończ z komunikatem i kodem ≠ 0
# [ ] jeśli quiet → zminimalizuj wypisy
# [ ] wersja narzędzia może być brana z pyproject (na razie wpisz placeholder)
# [ ] zostaw TODO pod integrację z parserem/aggregatorem/reporterem w kolejnych lekcjach
