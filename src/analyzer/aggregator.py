"""
Module: aggregator.py
Cel: Agregacja rekordów sparsowanych z Apache Combined (top-N, statusy, metody, histogram czasu).
Public API:
  - class StatsAggregator:
      - ingest(record: dict) -> None
      - snapshot_top_ips(n: int) -> list[tuple[str, int]]
      - snapshot_top_paths(n: int) -> list[tuple[str, int]]
      - snapshot_status_counts() -> dict[int, int]
      - snapshot_method_counts() -> dict[str, int]
      - snapshot_time_histogram(bucket: str) -> dict[str, int]  # bucket: 'hour'|'day'
      - reset() -> None
Wyjątki:
  - ValueError: niepoprawny bucket, n<1 itp.
Bezpieczeństwo:
  - Pamięć: wzrost ~O(unikatowych kluczy); brak przechowywania PII (UA/referrer nieagregowane domyślnie).
  - Brak eval/exec; wejście to wynik parse_line (zwalidowany).
  - Limity: defensywne limity n, ochrona przed n<=0.
TODO (lekcja 4):
  [ ] Zaprojektować wewnętrzne liczniki (Counter): by_ip, by_path, by_status, by_method, by_time
  [ ] Normalizacja klucza czasu: 'YYYY-MM-DDTHH:00' dla 'hour', 'YYYY-MM-DD' dla 'day'
  [ ] Implementacja ingest(record) – inkrementacja liczników
  [ ] Implementacja snapshot_* – zwroty posortowane malejąco (top-N)
  [ ] reset() – czyszczenie liczników
  [ ] (opcjonalnie) limit maksymalnej liczby unikatowych kluczy
"""
# imports: stdlib -> third-party -> local
from __future__ import annotations

from typing import Optional, Iterable, Iterator

class StatsAggregator:
    def __init__(self) -> None: ...
    def ingest(self, record: dict) -> None: ...
    def snapshot_top_ips(self, n: int) -> list[tuple[str, int]]: ...
    def snapshot_top_paths(self, n: int) -> list[tuple[str, int]]: ...
    def snapshot_status_counts(self) -> dict[int, int]: ...
    def snapshot_method_counts(self) -> dict[str, int]: ...
    def snapshot_time_histogram(self, bucket: str = "hour") -> dict[str, int]: ...
    def reset(self) -> None: ...
