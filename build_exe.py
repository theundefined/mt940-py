import PyInstaller.__main__
import os
import platform

def build():
    # Ścieżka do głównego pliku wykonywalnego
    main_path = os.path.join("src", "mt940_py", "main.py")
    
    # Argumenty PyInstallera
    args = [
        main_path,
        "--onefile",           # Jeden plik EXE
        "--noconsole",         # Brak konsoli (bo mamy GUI)
        "--name=MT940-Converter", # Nazwa pliku
        "--clean",
        # W przypadku customtkinter musimy dodać bibliotekę do ścieżki (jeśli są problemy)
        "--add-data=venv/lib/python3.12/site-packages/customtkinter:customtkinter/" if platform.system() == "Linux" else "",
    ]
    
    # Filtrujemy puste argumenty
    args = [a for a in args if a]
    
    print(f"Rozpoczynam budowanie dla systemu: {platform.system()}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
