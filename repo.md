
---

# 1) Gałęzie (branches): po co i jak

## Minimalny model

* `main` – **zawsze stabilny kod** (zielony CI). Tu trafia tylko to, co przeszło testy.
* `feature/<nazwa>` – **pracujesz tu nad jedną rzeczą** (np. `feature/cli`, `feature/parser`).

> (Opcjonalnie) `dev` – wspólna gałąź integracyjna; na solo nie jest konieczna.

## Jak to zrobić

```bash
# Jesteś w katalogu projektu
git init                     # jeśli jeszcze nie zrobiłeś
git branch -M main           # nazwa głównej gałęzi = main
git checkout -b feature/cli  # zaczynasz pracę nad CLI
```

Pracujesz → commitujesz → pushujesz **na feature** → robisz **Pull Request (PR)** do `main`.

---

# 2) Commity: nazewnictwo i praktyka

## Format komunikatu (krótko i jasno)

```
<typ>: <zwięzły opis>
```

**Typy, których używaj:**

* `feat:` – nowa funkcja (np. pierwsza wersja CLI)
* `fix:` – poprawka błędu
* `docs:` – dokumentacja (README, komentarze)
* `test:` – testy
* `refactor:` – zmiany w kodzie bez zmiany zachowania
* `chore:` – porządki, .gitignore, konfiguracje

## Przykłady dobrych commitów

```bash
git add .
git commit -m "chore: scaffold project structure and .gitignore"
git commit -m "docs: add CLI spec and usage examples to README"
git commit -m "feat(cli): add basic argument definitions and validation plan"
git commit -m "test(parser): add fixtures for combined log format"
```

**Zasady:**

* **Małe commity** (1 logiczna zmiana = 1 commit).
* Wiadomo „co, po co”. Unikaj „update”, „poprawki2”.

---

# 3) Pull Request (PR): jak i po co

PR to „prośba o włączenie” Twojej gałęzi do `main`.
W PR-ze:

* GitHub uruchamia **CI** (lint/test).
* Widać listę zmian, opis, checklistę.
* Możesz prosić o review (nawet sam sobie, jako kontrola).

## Jak to zrobić

```bash
git push -u origin feature/cli     # pierwszy push nowej gałęzi
# potem w UI GitHuba: "Compare & pull request"
```

### Szablon opisu PR (wklejaj w GitHubie)

**Tytuł:** `feat(cli): initial CLI options and help`
**Opis:**

* **Co:** dodano sekcję Specyfikacja CLI w README, założono plik `cli.py`.
* **Po co:** przygotowanie do implementacji argumentów i parsowania.
* **Jak testować:** przejrzeć README → sekcja CLI; sprawdzić, czy struktura repo jest zgodna.
* **Checklist:**

  * [ ] README zaktualizowane
  * [ ] Lint/test przechodzi lokalnie
  * [ ] Zmiany logicznie spójne (1 feature)

Po **zielonym CI** robisz merge (najlepiej **Squash & Merge** — historia w `main` będzie czysta).

---

# 4) Ustawienia na GitHubie (branch protection)

*(Opcjonalnie, ale polecam — zapobiegnie przypadkowemu zepsuciu `main`)*

1. Repo → **Settings** → **Branches** → *Add branch protection rule*.
2. Branch name pattern: `main`.
3. Zaznacz:

   * **Require a pull request before merging**
   * **Require status checks to pass before merging** (wskaż workflow z CI)
   * (Opcjonalnie) **Dismiss stale pull request approvals…**
4. Zapisz.

Efekt: nic nie trafi do `main` bez PR i zielonego pipeline’u.

---

# 5) Typowy dzień pracy (twój „flow”)

1. **Utwórz** gałąź: `git checkout -b feature/parser`.
2. **Rób małe commity** co \~30–60 min pracy.
3. **Pushuj**: `git push -u origin feature/parser`.
4. **Otwórz PR** do `main` (z opisem i checklistą).
5. Sprawdź **CI** (musi być zielone).
6. **Squash & Merge** do `main`.
7. **Usuń** gałąź feature w repo (GitHub pyta automatycznie).
8. Lokalnie: `git checkout main` → `git pull`.

---

# 6) Rebase vs Merge (kiedy co)

* Pracujesz solo? **Merge** (Squash & Merge w PR) w zupełności wystarczy.
* Masz wiele równoległych gałęzi i zmiany w `main`? Czasem:

  ```bash
  git checkout feature/parser
  git fetch origin
  git rebase origin/main   # wciąga zmiany z main na czysto
  # rozwiąż konflikty, kontynuuj rebase
  git push --force-with-lease
  ```

  Jeśli hasło „rebase” Cię stresuje — **po prostu merguj** `main` do feature:

  ```bash
  git merge origin/main
  ```

Najważniejsze: **nie zostawiaj konfliktów na koniec**, aktualizuj feature regularnie.

---

# 7) Najczęstsze potknięcia

* **Praca na `main`** — nie rób. Zawsze `feature/*`.
* **Wielkie PR-y** — trudno zreviewować, łatwo o bugi. Lepiej kilka małych.
* **Ogólniki w commitach** — utrudniają debug. Pisz, *co* i *po co*.
* **Brak `.gitignore`** — zaśmiecasz repo (venv, cache, raporty).

---

# 8) Minimalne komendy, których potrzebujesz

```bash
# start
git init
git add .
git commit -m "chore: initial scaffold"
git branch -M main
git remote add origin <URL_DO_REPO>
git push -u origin main

# nowa funkcja
git checkout -b feature/cli
# ... zmiany ...
git add .
git commit -m "feat(cli): add CLI spec to README"
git push -u origin feature/cli
# otwórz PR w GitHub

# po merge do main
git checkout main
git pull
```

---

# 9) Co to daje w twoim projekcie

* Każdy etap z „lekcji” staje się **osobną gałęzią feature** → czysto i przewidywalnie.
* CI/CD w PR pilnuje jakości (lint/test, potem artefakty raportów).
* Na rozmowie rekrutacyjnej pokazujesz **profesjonalny workflow**, a nie tylko zlepek plików.

---


