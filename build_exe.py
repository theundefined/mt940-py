import PyInstaller.__main__
import os
import platform
import customtkinter

def build():
    # Główne ścieżki
    main_path = os.path.join("src", "mt940_py", "main.py")
    
    # Dynamiczne znajdowanie ścieżki do customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Separator: Windows ';', Linux ':'
    separator = ";" if platform.system() == "Windows" else ":"
    add_data_arg = f"{ctk_path}{separator}customtkinter"
    
    args = [
        main_path,
        "--onefile",
        "--noconsole",
        "--name=MT940-Converter",
        "--clean",
        f"--add-data={add_data_arg}",
    ]
    
    # Komunikaty bez polskich znaków (bezpieczeństwo kodowania konsoli)
    print(f"--- Starting build for: {platform.system()} ---")
    print(f"CustomTkinter path: {ctk_path}")
    print(f"Arguments: {args}")
    
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
