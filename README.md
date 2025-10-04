# Analityka logów HTTP w Pythonie + CI/CD

Krótki opis: narzędzie CLI do **parsowania** logów HTTP (Apache/Nginx), **agregowania statystyk** (top IP, błędy 4xx/5xx, najpopularniejsze ścieżki, rozkład w czasie) oraz **generowania raportów** (TXT/CSV/JSON). Projekt z testami (`pytest`), lintingiem i pipeline’em **GitHub Actions**.

---

## Spis treści
- [Analityka logów HTTP w Pythonie + CI/CD](#analityka-logów-http-w-pythonie--cicd)
  - [Spis treści](#spis-treści)
  - [Cele projektu](#cele-projektu)
  - [Funkcjonalności](#funkcjonalności)
  - [Architektura i przepływ](#architektura-i-przepływ)
  - [Struktura repozytorium](#struktura-repozytorium)
  - [Dane wejściowe (logi)](#dane-wejściowe-logi)
  - [Instrukcja uruchomienia](#instrukcja-uruchomienia)
  - [Specyfikacja CLI](#specyfikacja-cli)
    - [Przykłady użycia](#przykłady-użycia)
  - [Testy i jakość](#testy-i-jakość)
  - [CI/CD (GitHub Actions)](#cicd-github-actions)
  - [Bezpieczeństwo i wydajność](#bezpieczeństwo-i-wydajność)
  - [Przykładowe wyniki](#przykładowe-wyniki)
  - [Roadmapa / TODO](#roadmapa--todo)
  - [Czego się nauczyłem](#czego-się-nauczyłem)
  - [Licencja](#licencja)
  - [Parser (Apache Combined)](#parser-apache-combined)
    - [Przykład (fragment)](#przykład-fragment)
  - [Aggregator](#aggregator)

---

## Cele projektu
- Parsowanie logów HTTP (Common/Combined).
- Agregacja kluczowych metryk (IP, statusy, metody, ścieżki, rozkład czasowy).
- Generowanie raportów: **TXT**, **CSV** i/lub **JSON**.
- Testy jednostkowe i linting; pipeline **CI** (GitHub Actions).
- Czytelna struktura repo i dokumentacja.

**Zakres poza projektem:** brak UI, brak rozproszenia (Spark/Kafka), DB tylko opcjonalnie (SQLite).

---

## Funkcjonalności
- CLI z opcjami: `--input`, `--outdir`, `--format`, `--top`, `--time-bucket`, `--limit`.
- Obsługa błędnych linii (logowanie do `errors.log`, zliczanie).
- Statystyki:
  - Top N: IP, ścieżki, user-agenty (opcjonalnie),
  - Statusy: 2xx/3xx/4xx/5xx + kody,
  - Metody: GET/POST/…,
  - Czas: per godzina/dzień.
- Raporty: `reports/report.txt` + `reports/report.csv/json`.
- (Opcjonalnie) Wykresy PNG/HTML i SQLite.

---

## Architektura i przepływ
1. **Reader** → strumieniowe czytanie pliku (linia po linii).
2. **Parser** → regex + walidacje (IP, timestamp, status, metoda).
3. **Aggregator** → liczniki (Counter), histogram czasu, top listy.
4. **Reporter** → TXT/CSV/JSON (ew. wykresy).
5. **CLI** → spina wszystko; kody wyjścia, logi błędów.

---

## Struktura repozytorium
```
├─ src/
│ ├─ analyzer/
│ │ ├─ io_reader.py
│ │ ├─ parser.py
│ │ ├─ aggregator.py
│ │ ├─ reporter.py
│ │ └─ cli.py
│ └─ main.py
├─ tests/
│ ├─ test_parser.py
│ ├─ test_aggregator.py
│ ├─ test_reporter.py
│ └─ fixtures/
├─ data/
│ ├─ access_small.log
│ └─ corrupted.log
├─ reports/ # generowane w runtime (nie commituj dużych)
├─ .github/workflows/ci.yml
├─ pyproject.toml # albo requirements.txt
├─ .gitignore
├─ README.md
└─ LICENSE
```

---

## Dane wejściowe (logi)
- Format: **Apache Combined Log Format**.
- Przykład linii: `ip - - [timestamp] "METHOD URL PROTO" status bytes "referrer" "user-agent"`
- Próbki: `data/access_small.log`, `data/corrupted.log`.

---

## Instrukcja uruchomienia
1. Utwórz wirtualne środowisko i zainstaluj zależności (patrz `pyproject.toml`/`requirements.txt`).
2. Umieść plik logów w `data/`.
3. Uruchom CLI wskazując `--input` i format raportu `--format`.
4. Sprawdź wyniki w katalogu `reports/`.

> Szczegóły użycia i wszystkie opcje zobaczysz po wywołaniu `--help`.

---
## Specyfikacja CLI

| Flaga / Argument  | Typ / Dozwolone wartości | Wymagane | Domyślne  | Opis |
|-------------------|--------------------------|----------|-----------|------|
| `--input`         | ścieżka                  | TAK      | —         | Ścieżka do pliku logów Apache/Nginx (format Combined). |
| `--outdir`        | ścieżka                  | nie      | `./reports` | Katalog na raporty; tworzony automatycznie jeśli nie istnieje. |
| `--format`        | `txt`, `csv`, `json`     | nie      | `txt`     | Format raportu. |
| `--top`           | liczba całkowita ≥ 1     | nie      | `10`      | Liczba pozycji w rankingach. |
| `--time-bucket`   | `hour`, `day`            | nie      | `hour`    | Jak grupować statystyki czasowe. |
| `--limit`         | liczba całkowita ≥ 1     | nie      | brak      | Maksymalna liczba linii do przetworzenia (debug/testy). |
| `--fail-policy`   | `skip`, `strict`         | nie      | `skip`    | Jak reagować na błędne linie (`skip` – pomija, `strict` – kończy program). |
| `--encoding`      | string                   | nie      | `utf-8`   | Dekodowanie pliku. |
| `--quiet`         | flaga                    | nie      | `false`   | Tryb cichy – minimum logów w konsoli. |
| `--version`       | flaga                    | nie      | —         | Wyświetla wersję narzędzia i kończy działanie. |

### Przykłady użycia

1. **Raport TXT z domyślnymi ustawieniami**  
   ```bash
   python -m src.main --input data/access_small.log
   ```
---

## Testy i jakość
- **Testy:** `pytest` (parser, aggregator, reporter, smoke test CLI).
- **Linting:** `ruff`/`flake8`.
- **(Opcjonalnie)** Typowanie: `mypy`.
- **(Opcjonalnie)** Skan bezpieczeństwa: `bandit`.

---

## CI/CD (GitHub Actions)
- Pipeline uruchamia się na `push`/`pull_request`:
  1) setup Pythona  
  2) instalacja zależności  
  3) linting  
  4) testy  
  5) generowanie przykładowych raportów z `data/access_small.log`  
  6) **upload artefaktów** (raporty)
- Status pipeline’u: ![CI](https://img.shields.io/badge/CI-passing-brightgreen) *(podmień na właściwy badge z Actions)*

---

## Bezpieczeństwo i wydajność
- Walidacja pól (status, IP, timestamp), unikanie `eval`.
- Błędne linie: logowane i zliczane; narzędzie się nie wywraca.
- Przetwarzanie strumieniowe (niskie zużycie RAM na dużych plikach).

---

## Przykładowe wyniki
*(Wstaw screeny/zrzuty raportów — np. fragment `report.txt` i lista plików w `reports/`).*

---

## Roadmapa / TODO
- [ ] Wersja podstawowa (TXT/CSV, top N IP/ścieżek, statusy).
- [ ] JSON i wykresy PNG/HTML.
- [ ] Konfiguracja YAML (progi, wzorce).
- [ ] SQLite.
- [ ] Dockerfile + GitHub Release.

---

## Czego się nauczyłem
{{W punktach opisz 3–5 rzeczy: regex, Counter, strumieniowe IO, projektowanie CLI, CI w Actions, debugowanie parsowania…}}

---

## Licencja
MIT

## Parser (Apache Combined)

Parser obsługuje format **Apache Combined** i zwraca słownik z polami:
`remote_host, identd, user, ts (UTC, tz‑aware), method, path, protocol, status, size, referrer, user_agent`.

**Walidacje i normalizacje:**
- `remote_host`: IPv4 (0–255 w oktetach); w przyszłości planowana obsługa hostnames/IPv6.
- `ts`: `DD/Mon/YYYY:HH:MM:SS ±HHMM` → `datetime` w **UTC** (uwzględnia offset).
- `method`: whitelist `{GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH, CONNECT, TRACE}`.
- `status`: `100..599`.
- `size`: liczba nieujemna lub `-` → `None`.
- `protocol`: `HTTP/1.0`, `HTTP/1.1`, `HTTP/2`, `HTTP/3` lub `None`.
- `referrer`, `user_agent`: `-` → `None`; obsługa escapowanych cudzysłowów.

**Polityka błędów (`--fail-policy`)**
- `skip` *(domyślnie)* — błędna linia jest pomijana; licznik błędów rośnie; **logger.warning** otrzymuje krótką diagnozę.
- `strict` — program przerywa działanie (**ValueError** na pierwszej błędnej linii).

### Przykład (fragment)
Wejście (`data/access_small.log`):  
– linie poprawne (200/404/302…),  
– linie błędne w `data/corrupted.log` (np. brak `[]`, zła godzina `99`, `status=999`).  

> Parser jest wpięty do CLI (lekcja 6); w tej lekcji (3) przygotowujemy kontrakt i testy.

## Aggregator

Warstwa agregacji przetwarza strumień rekordów zwróconych przez parser i utrzymuje liczniki:
- **Top N IP** i **Top N ścieżek**,
- **Rozkład statusów** (100–599) oraz **metod HTTP**,
- **Histogram czasu** z krokiem `hour` lub `day`.

**Kontrakt (API)**  
Wewnętrznie korzystamy z klasy `StatsAggregator` z metodami:
`ingest(record)`, `snapshot_top_ips(n)`, `snapshot_top_paths(n)`, `snapshot_status_counts()`,
`snapshot_method_counts()`, `snapshot_time_histogram(bucket)`, `reset()`.

**Założenia wydajnościowe i bezpieczeństwa**  
Agregacja jest *online* – rekord po rekordzie, bez trzymania całych logów; pamięć rośnie ~O(unikatowych kluczy). Nie gromadzimy PII (UA/referrer) w licznikach. Brak `eval/exec`.

**Użycie w CLI**  
W tej lekcji przygotowaliśmy hooki w `cli.py` (TODO): po sparsowaniu linii wywoływana jest `ingest(...)`, a na końcu można wypisać podsumowanie (top‑N/status/metoda/histogram). Zapisy do plików (TXT/CSV/JSON) dodamy w **Lekcji 5**.

