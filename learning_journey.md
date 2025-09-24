# Learning Journey — Python Log Analyzer

> Krótkie notatki „co zrobiłem / czego się nauczyłem / jak rozwiązałem problemy”.
> Model pracy: **1 lekcja = 1 gałąź feature + PR**.

## Lekcja 1 — Scaffold & CLI (wstęp)
**Co zrobiłem:** postawiłem strukturę `src/`, `tests/`, wstępny `cli.py`, wejście `python -m src.main`.  
**Czego się nauczyłem:** Typer/Click, projektowanie interfejsu CLI, świadomy `main` (brak logiki biznesowej).  
**Problemy i rozwiązania:** importy pakietowe → decyzja o `src/` + (docelowo) `__init__.py`.  
**PR:** `feat/p2-lesson-01-scaffold-cli` → zielony smoke test CLI.  
**Pliki kluczowe:** `src/main.py`, `src/analyzer/cli.py`. 

## Lekcja 2 — Reader & smoke CLI
**Co zrobiłem:** strumieniowy odczyt linii (`io_reader.read_log_lines`), opcje `--input`, `--encoding`, `--limit`; testy I/O i CLI.  
**Czego się nauczyłem:** fallback kodowania (utf‑8→latin‑1), iteracyjne API, testy z `tmp_path`.  
**Problemy i rozwiązania:** test odwoływał się do `data/access_big.log` → decyzja: dodać plik **albo** przepisać test na `tmp_path`.  
**PR:** `feat/p2-lesson-02-reader-cli`; **TODO:** uporządkować test z `access_big.log`.  
**Pliki kluczowe:** `src/analyzer/io_reader.py`, `tests/test_io_reader.py`, `tests/test_cli.py`. 

## Lekcja 3 — Parser (Apache Combined)
**Co zrobiłem:** kontrakt `parse_line(line, fail_policy="skip") -> dict|None`, twarde walidacje (IPv4, status, metoda), `datetime` UTC, limit długości linii.  
**Czego się nauczyłem:** precyzyjne regexy z `re.VERBOSE`, budowa `datetime` z offsetem i `astimezone(UTC)`, bezpieczne logowanie (bez PII).  
**Problemy i rozwiązania:** spójność wzorców protokołu (`HTTP/1.1` vs `HTTP/2`) → jeden wzorzec `HTTP/\d(?:\.\d)?`.  
**PR:** `feat/p2-lesson-03-parser`.  
**Dalej:** dodać testy parsera; w CLI na razie tylko TODO pod integrację.  
**Dane testowe:** `data/access_small.log` (good), `data/corrupted.log` (bad). 
