# mt940-py

Biblioteka i narzędzie do walidacji oraz konwersji wyciągów bankowych do formatu MT940 (wariant polski ZBP).

## Główne funkcjonalności
- **Walidacja**: Sprawdzanie spójności logicznej plików MT940 (sumy kontrolne sald i transakcji).
- **Konwersja**: Tworzenie plików MT940 z wyciągów CSV (obecnie wspiera mBank).
- **Eksport**: Konwersja MT940 do czytelnego formatu CSV.
- **Interfejsy**: Biblioteka Python, CLI oraz nowoczesne GUI (CustomTkinter).

## Instalacja
```bash
pip install mt940-py
```

## Użycie CLI
```bash
mt940-val gui        # Uruchomienie interfejsu graficznego
mt940-val validate   # Walidacja pliku
mt940-val convert    # Konwersja CSV -> MT940
mt940-val export     # Eksport MT940 -> CSV
```

## Rozwój
Projekt używa `black`, `ruff` i `pytest` do zapewnienia wysokiej jakości kodu.
