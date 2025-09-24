"""
Module: parser.py
Cel:
  Parsowanie linii logów HTTP (Apache Combined) do znormalizowanego słownika.
  Wynik: typy poprawne, wartości zmapowane ('-' -> None), czas tz-aware w UTC.

Public API:
  - parse_line(line: str, fail_policy: str = "skip") -> dict | None

Kontrakt wyniku:
  {
    "remote_host": str,          # IPv4 (kanoniczne, 0..255 na oktet, bez wiodących zer)
    "identd": str | None,        # '-' -> None
    "user": str | None,          # '-' -> None
    "ts": datetime,              # tz-aware, znormalizowany do UTC
    "method": str,               # z whitelisty: GET/POST/PUT/DELETE/HEAD/OPTIONS/PATCH/CONNECT/TRACE
    "path": str,                 # niepusta ścieżka/URL bez spacji
    "protocol": str | None,      # 'HTTP/1.0', 'HTTP/1.1', 'HTTP/2' lub 'HTTP/3' (kanoniczne), albo None
    "status": int,               # 100..599
    "size": int | None,          # '-' -> None; ASCII cyfry, wiodące zera dozwolone (normalizowane)
    "referrer": str | None,      # '-' -> None; dopuszcza escapowane cudzysłowy
    "user_agent": str | None     # '-' -> None; dopuszcza escapowane cudzysłowy
  }

Polityki i bezpieczeństwo:
  - Limit długości linii: 16 MiB (MAX_LINE_LEN) — ochrona przed DoS.
  - Brak eval/exec, brak wykonywania danych wejściowych.
  - Walidacje: zakresy liczb, kształt i zakres IPv4, status 100..599, metody z whitelisty,
    timestamp zgodny z 'DD/Mon/YYYY:HH:MM:SS ±HHMM' -> UTC.
  - Obsługa błędów (fail_policy):
      * "skip"   -> zwróć None, zaloguj ostrzeżenie (bez PII),
      * "strict" -> rzuć ValueError z krótką diagnozą.
  - Logowanie: świadome, bez pełnych UA/referrer; komunikaty krótkie.

Decyzje implementacyjne (stan obecny):
  - Metody HTTP: tylko CAPS (regex [A-Z]+), brak auto-upper — świadomie rygorystycznie.
  - IPv4: wymuszone już w głównym regexie (0..255, brak wiodących zer). Dodatkowy walidator
    is_ipv4 pozostaje w module jako centralny punkt polityki (na przyszłość).
  - Protocol: akceptujemy 'HTTP/1.0', 'HTTP/1.1', 'HTTP/2', 'HTTP/3'. (Ewent. kanonizacja 'HTTP/2.0' -> 'HTTP/2' w przyszłości.)
  - Size: '-'/'' -> None; inaczej ASCII cyfry (bez znaków +/-, spacji, przecinków); wiodące zera dozwolone (int(...) normalizuje).
  - Referrer/User-Agent: w cudzysłowie; obsługujemy `\"` -> `"`. (Rozszerzenie o `\\` -> `\` jako przyszły szlif.)

Walidacja parametrów wejścia:
  - fail_policy akceptuje {"skip","strict"}; inne wartości będą traktowane jak "skip" (i logowane ostrzeżenie).
    (Można utrzymać jako guard na początku parse_line.)

Wyjątki:
  - ValueError w trybie "strict" dla: złej składni, złych zakresów (IP, status, czas, offset), błędnego protokołu,
    size z niedozwolonymi znakami, przekroczonego limitu długości linii itp.

Roadmap / TODO (przyszłe szlify — nieblokujące):
  [ ] parse_request(method, path, protocol) — wyekstrahować obecną walidację z parse_line
      do osobnej funkcji (łatwiejsze testy jednostkowe). Jeśli nie planujemy — usunąć z TODO.
  [ ] fail_policy guard — asertywnie sprawdzić wartość; niepoprawne potraktować jak "skip" + warning.
  [ ] protocol canon — opcjonalnie kanonizować 'HTTP/2.0' -> 'HTTP/2' w wyniku.
  [ ] unescape(+): oprócz `\"` rozważyć `\\` -> `\` i tylko to (bez interpretowania \n, \t, \xNN).
  [ ] throttle logs w "skip" — przy bardzo dużych plikach ograniczyć warningi (np. co 1000) i dodać licznik podsumowujący.
  [ ] tests: dodać parametryczne testy całości parse_line (happy path + błędy per pole + polityka skip/strict).
  [ ] ścieżka: w razie potrzeby rozszerzyć walidację o dopuszczenie percent-encoding; nadal odrzucać białe znaki i znaki kontrolne.
  [ ] hostnames/IPv6 (jeśli kiedyś): poluzować regex na remote_host i użyć is_ipv4/alternatywnych walidatorów.

Notatki dla użytkowników modułu:
  - API publiczne: parse_line (i opcjonalnie MAX_LINE_LEN). Rozważ __all__ = ["parse_line", "MAX_LINE_LEN"].
  - Parser jest stateless; bezpieczny do użycia w strumieniach/CLI oraz w środowisku wielowątkowym.
"""
