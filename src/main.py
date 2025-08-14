# === ENTRYPOINT (src/main.py) ===
# Cel: punkt startowy aplikacji, uruchamia CLI:
#   python -m src.main [OPCJE]
#
# TODO:
# [ ] NIE dodawaj logiki biznesowej tutaj
# [ ] Cała logika w analyzer/cli.py i dalszych modułach
# [ ] Ten plik ma tylko wywołać app()

from analyzer.cli import app  # import z pakietu 'analyzer' (wewnątrz src)

if __name__ == "__main__":
    app()
