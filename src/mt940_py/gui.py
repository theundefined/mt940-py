import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from mt940_py.converter import MT940Converter
from mt940_py.validator import MT940Validator

# Ustawienia wyglądu
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MT940App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MT940-py: Konwerter i Walidator")
        self.geometry("600x450")

        self.converter = MT940Converter()
        self.validator = MT940Validator()

        # Układ siatki
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Nagłówek
        self.label = ctk.CTkLabel(self, text="Konwerter mBank CSV -> MT940", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Przyciski akcji
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.select_button = ctk.CTkButton(self.button_frame, text="Wybierz plik CSV (mBank)", command=self.select_file)
        self.select_button.grid(row=0, column=0, padx=10, pady=10)

        self.val_button = ctk.CTkButton(self.button_frame, text="Waliduj plik MT940", command=self.validate_mt940, fg_color="gray")
        self.val_button.grid(row=0, column=1, padx=10, pady=10)

        # Status pliku
        self.status_label = ctk.CTkLabel(self, text="Nie wybrano pliku", font=ctk.CTkFont(slant="italic"))
        self.status_label.grid(row=2, column=0, padx=20, pady=5)

        # Logi / Wyniki
        self.textbox = ctk.CTkTextbox(self, width=560)
        self.textbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.insert("0.0", "System gotowy.\n\n")

    def log(self, message: str):
        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz plik mBank CSV",
            filetypes=[("Pliki CSV", "*.csv"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            self.status_label.configure(text=f"Wybrano: {os.path.basename(file_path)}")
            self.process_conversion(file_path)

    def process_conversion(self, input_path: str):
        output_path = filedialog.asksaveasfilename(
            title="Zapisz jako MT940",
            defaultextension=".txt",
            initialfile=os.path.basename(input_path).replace(".csv", ".txt"),
            filetypes=[("Pliki tekstowe", "*.txt"), ("Pliki MT940", "*.sta"), ("Wszystkie pliki", "*.*")]
        )

        if not output_path:
            return

        try:
            self.log(f"Rozpoczynam konwersję: {os.path.basename(input_path)}...")
            with open(input_path, "r", encoding="cp1250", errors="replace") as f:
                content = f.read()
            
            mt940_content = self.converter.convert(content)
            # Zapisujemy jako UTF-8 z BOM (utf-8-sig)
            with open(output_path, "w", encoding="utf-8-sig") as f:
                f.write(mt940_content)
            
            self.log(f"SUCCESS: Zapisano do {output_path}")
            val_results = self.validator.validate_file(output_path)
            if val_results["is_valid"]:
                self.log(f"Walidacja OK: {val_results['statements_count']} wyciągów.")
                messagebox.showinfo("Sukces", "Konwersja zakończona pomyślnie!")
            else:
                self.log("BŁĄD WALIDACJI wygenerowanego pliku!")
                messagebox.showwarning("Uwaga", "Plik wygenerowany, ale zawiera błędy logiczne.")
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Błąd", str(e))

    def validate_mt940(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz plik MT940",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Pliki MT940", "*.sta"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            val_results = self.validator.validate_file(file_path)
            if val_results["is_valid"]:
                self.log(f"SUCCESS: Plik {os.path.basename(file_path)} poprawny.")
                messagebox.showinfo("OK", "Plik jest poprawny.")
            else:
                self.log(f"FAILURE: Plik {os.path.basename(file_path)} błędny.")
                messagebox.showerror("Błąd", "Plik zawiera błędy.")

def main():
    app = MT940App()
    app.mainloop()

if __name__ == "__main__":
    main()
