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

import typer
from typing_extensions import Annotated
from pathlib import Path
from enum import Enum
from typing import Optional
from .io_reader import read_log_lines


# ===== Aplikacja =====
app = typer.Typer(no_args_is_help=True)


# ===== Pomocnicze: pobieranie wersji z pyproject.toml =====
def get_version() -> str:
    """
    Czyta wersję z pyproject.toml (tool.poetry.version).
    Działa również w package-mode=false.
    """
    try:
        import tomllib  # python 3.11+

        root = Path(__file__).resolve().parents[2]
        pyproj = root / "pyproject.toml"

        with pyproj.open("rb") as f:
            data = tomllib.load(f)
            return data["tool"]["poetry"]["version"]

    except Exception:
        return "Error has occured, version: 0.0.0"


# ===== Globalny callback: --version działa bez wymagania --input =====
@app.callback(invoke_without_command=True)
def app_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version", help="Wyświetl wersję narzędzia i zakończ",
            is_flag=True,
            is_eager=True, # Uruchom zanim wejdziemy w komendę
        )
    ] = False,
):
    if version:
        typer.echo(f"python-log-analyzer {get_version()}")
        raise typer.Exit(code=0)

# ===== Enum (placeholder) =====
class ReportFormat(str, Enum):
    TXT = "txt"
    CSV = "csv"
    JSON = "json"

@app.command()
def main(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            help="Ścieżka do pliku logów (Apache/Nginx)",
            exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
        )
    ],

    encoding: Annotated[
        str,
        typer.Option("--encoding", help="Kodowanie pliku logów")] = "utf-8",

    limit: Annotated[
        int,
        typer.Option("--limit", help="Limit linii (0 = bez limitu)")] = 0,

    # PlaceHoldery
    preview_cap: Annotated[int, typer.Option("--preview-cap", help="Podgląd: pokaż pierwsze N linii (0=wyłączone)")] = 0,
    outdir_path: Annotated[Path, typer.Option("--outdir", help="Katalog raportów")] = Path("./reports"),
    format: Annotated[ReportFormat, typer.Option(help="Format raportu: txt|csv|json")] = ReportFormat.TXT,
    top: Annotated[int, typer.Option("--top", help="Ilość pierwszych linijek.")] = 10,
    time_bucket: Annotated[str, typer.Option("--time-bucket", help="Jednostka grupowania czasu (hour/day)")] = "hour",
    fail_policy: Annotated[str, typer.Option("--fail-policy", help="Polityka błędów: skip/strict")] = "skip",
    quiet: Annotated[bool, typer.Option("--quiet", help="Tryb cichy - minimum logów", is_flag=True)] = False,

    ):

    eff_limit: Optional[int] = None if (limit == 0 or limit < 0) else limit

    try:
        count = 0
        for line in read_log_lines(input_path, encoding=encoding, limit=eff_limit):
            count += 1
            if not quiet and count <= preview_cap:
                typer.echo(f"[{count}] {line}")

        if not quiet:
            typer.echo(f"Wczytano {count} linii z: {input_path}")

        raise typer.Exit(code=0)

    except FileNotFoundError as e:
        typer.echo(f"Błąd: plik nie istnieje: {e}", err=True)
        raise typer.Exit(code=2)

    except PermissionError as e:
        typer.echo(f"Brak uprawnień do pliku: {e}", err=True)
        raise typer.Exit(code=3)

    except UnicodeDecodeError as e:
        typer.echo(f"Błąd kodowania pliku ({encoding}), Spróbuj innym kodowaniem. Szczegóły: {e}", err=True)
        raise typer.Exit(code=4)

    except OSError as e:
        typer.echo(f"Błąd systemowy podczas odczytu pliku: {e}", err=True)
        raise typer.Exit(code=5)


if __name__ == "__main__":
    app()
