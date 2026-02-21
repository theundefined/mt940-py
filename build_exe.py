import PyInstaller.__main__
import os
import platform
import customtkinter

def build():
    # Ścieżka do głównego pliku wykonywalnego
    main_path = os.path.join("src", "mt940_py", "main.py")
    
    # Dynamiczne znajdowanie ścieżki do customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Separator zależy od systemu (Windows używa ';', Linux ':')
    separator = ";" if platform.system() == "Windows" else ":"
    
    # Format argumentu --add-data: "źródło:cel"
    add_data_arg = f"{ctk_path}{separator}customtkinter"
    
    # Argumenty PyInstallera
    args = [
        main_path,
        "--onefile",                # Jeden plik EXE
        "--noconsole",              # Brak konsoli (GUI)
        "--name=MT940-Converter",   # Nazwa pliku wynikowego
        "--clean",                  # Wyczyść cache
        f"--add-data={add_data_arg}", # Dodaj pliki customtkinter
        # Opcjonalnie: Dodaj ikonę jeśli istnieje
        # "--icon=icon.ico", 
    ]
    
    print(f"--- Rozpoczynam budowanie dla systemu: {platform.system()} ---")
    print(f"Ścieżka CustomTkinter: {ctk_path}")
    print(f"Argumenty: {args}")
    
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
