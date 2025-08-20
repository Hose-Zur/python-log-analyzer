# === TESTY CLI (Typer CliRunner) ===
# Cel: smoke/E2E zachowanie CLI.
#
# WYMAGANIA:
# - --help: exit 0 + "Usage"
# - --version: exit 0 + nazwa/wersja
# - main --input <plik>: exit 0 + "Wczytano N linii"
# - main --input <brak_pliku>: exit 2 (walidacja Click) + komunikat błędu
# - main --limit 3: exit 0 + "Wczytano 3 linii"
#
# TODO:
# [x] test_help_ok
# [x] test_version_ok
# [x] test_cli_success (tmp_path)
# [x] test_limit_3 (tmp_path)
# [x] test_file_missing (exit_code==2 + komunikat)
# [ ] (opcjonalnie) test_quiet (brak preview/podsumowania na stdout)
# [ ] (opcjonalnie) mix_stderr=False i osobna asercja stderr


from typer.testing import CliRunner
from click.utils import strip_ansi
from src.analyzer.cli import app
from pathlib import Path
import re

runner = CliRunner()

def test_help_ok():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cli_success(tmp_path):
    # 1. Stwórz plik testowy
    file_path = tmp_path / "test.log"
    file_path.write_text("line1\nline2\nline3\nline4")

    # 2. Uruchom CLI
    result = runner.invoke(app, ["main", "--input", str(file_path)])

    # 3. Sprawdź wynik
    assert result.exit_code == 0
    assert "Wczytano 4 linii" in result.stdout  

def test_version_ok():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "python-log-analyzer" in result.stdout

def test_limit_3(tmp_path):
    file_path = tmp_path / "test_limit.log"
    file_path.write_text("a\nb\nc\nd\ne\nf")

    result = runner.invoke(app, ["main", "--input", str(file_path), "--limit", "3"])

    assert result.exit_code == 0
    assert "Wczytano 3 linii" in result.stdout

def test_file_missing():
    path = Path("data/__nope__.log")
    result = runner.invoke(app, ["main", "--input", str(path)])

    assert result.exit_code == 2

    msg = strip_ansi(result.stderr or result.output or "")
    assert re.search(r"(does not exist|Invalid value.*--input|nie istnieje|File not found)", msg)
    # stderr w CliRunner trafia do .stderr ORAZ często do .output — sprawdź lokalnie co zwraca

