"""
Zmiana (lekcja 3): przygotowanie integracji parsera.
- W 'main(...)' po pętli read_log_lines(...) dodaj:
  * wybór polityki błędów z --fail-policy (skip|strict),
  * wywołanie parse_line(line, fail_policy=...),
  * zliczanie: parsed_ok, parsed_bad,
  * (opcjonalnie) preview pierwszych K sparsowanych rekordów w trybie nie-quiet.
- Nie implementuj raportów — tylko tel. metryki i sumaryczny stdout.
- Zostaw wyraźne TODO pod wpięcie 'aggregator' w lekcji 4.
"""
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
from .parser import parse_line


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

class FailPolicy(str, Enum):
    SKIP = "skip"
    STRICT = "strict"

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

    fail_policy: Annotated[
        FailPolicy,
        typer.Option("--fail-policy", help="Polityka błędów: skip/strict")] = FailPolicy.SKIP,
    # PlaceHoldery
    preview_cap: Annotated[int, typer.Option("--preview-cap", help="Podgląd: pokaż pierwsze N linii (0=wyłączone)")] = 0,
    outdir_path: Annotated[Path, typer.Option("--outdir", help="Katalog raportów")] = Path("./reports"),
    format: Annotated[ReportFormat, typer.Option(help="Format raportu: txt|csv|json")] = ReportFormat.TXT,
    top: Annotated[int, typer.Option("--top", help="Ilość pierwszych linijek.")] = 10,
    time_bucket: Annotated[str, typer.Option("--time-bucket", help="Jednostka grupowania czasu (hour/day)")] = "hour",
    quiet: Annotated[bool, typer.Option("--quiet", help="Tryb cichy - minimum logów")] = False,

    ):

    eff_limit: Optional[int] = None if (limit == 0 or limit < 0) else limit

    try:
        count = 0
        parsed_ok = 0
        parsed_bad = 0
        parsed_preview_shown = 0 #licznik sparsowanych pokazanych w podglądzie

        # 1) weź "wartość" enuma albo zamień na string
        policy = (fail_policy.value if isinstance(fail_policy, Enum) else str(fail_policy))
        
        # 2) zrób małe litery
        policy = policy.lower()
        
        for line in read_log_lines(input_path, encoding=encoding, limit=eff_limit):
            count += 1
           
            if not quiet and preview_cap > 0 and count <= preview_cap:
                typer.echo(f"[{count}] {line}")

            try:
                rec = parse_line(line, fail_policy=policy)
            
                if rec is not None:
                    parsed_ok +=1

                    if not quiet and preview_cap > 0 and parsed_preview_shown < preview_cap: 
                    #!r → używa repr(rec) (techniczny, „debugowy” zapis obiektu)
                        typer.echo(f"[parsed {parsed_ok}] {rec!r}")
                        parsed_preview_shown += 1
                
                else:
                    parsed_bad += 1
                    if policy == "strict":
                        typer.echo(f"Błąd parsowania (None) w linii {count}", err=True)
                        raise typer.Exit(code=1)
            except Exception as e:
                parsed_bad += 1
                if policy == "strict":
                    typer.echo(f"Błąd parsowania w linii {count}: {e}",  err=True)
                    raise typer.Exit(code=1)
                else:
                    if not quiet:
                        typer.echo(f"(skip) Błąd parsowania w linii {count}: {e}", err=True)

                

        typer.echo(f"Wczytano {count} linii z: {input_path}")
        typer.echo(f"Poprawnie sparsowane: {parsed_ok}")
        typer.echo(f"Błędnie sparsowane: {parsed_bad}")

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
