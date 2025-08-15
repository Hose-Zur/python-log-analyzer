# === TESTY CLI (tests/test_cli.py) ===
# Cel: smoke testy komendy CLI: statusy wyjścia i podstawowe komunikaty.

# TODO:
# [ ] zaimportuj app z analyzer.cli
# [ ] użyj typer.testing import CliRunner
# [ ] test: --version -> kod 0
# [ ] test: poprawny --input -> kod 0
# [ ] test: brak pliku -> kod 2 i błąd na stderr
# [ ] test: --limit 3 -> w output powinno być "Wczytano 3 linii" (gdy preview_cap=0, to może być tylko podsumowanie)

# PRZYKŁADOWE KROKI (pseudo):
#
# from typer.testing import CliRunner
# from analyzer.cli import app
# from pathlib import Path
#
# runner = CliRunner()
#
# def test_version_ok():
#     result = runner.invoke(app, ["--version"])
#     assert result.exit_code == 0
#     assert "python-log-analyzer" in result.stdout
#
# def test_analyze_ok():
#     path = Path("data/access_small.log")
#     result = runner.invoke(app, ["main", "--input", str(path)])
#     assert result.exit_code == 0
#     assert "Wczytano" in result.stdout
#
# def test_file_missing():
#     path = Path("data/__nope__.log")
#     result = runner.invoke(app, ["main", "--input", str(path)])
#     assert result.exit_code == 2
#     # stderr w CliRunner trafia do .stderr ORAZ często do .output — sprawdź lokalnie co zwraca
#
# def test_limit_3():
#     path = Path("data/access_small.log")
#     result = runner.invoke(app, ["main", "--input", str(path), "--limit", "3"])
#     assert result.exit_code == 0
#     assert "Wczytano 3 linii" in result.stdout
