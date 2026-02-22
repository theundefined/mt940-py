import csv
import datetime
import io
import re
from typing import List

class MT940Converter:
    """Konwerter plików CSV (mBank) do formatu MT940 (ZBP) zgodnego z mBank/Insert."""

    def __init__(self, encoding: str = "cp1250") -> None:
        self.encoding = encoding

    def _clean_amount_str(self, val: str) -> str:
        if not val:
            return "0.0"
        cleaned = val.replace(" PLN", "").replace(" ", "").replace(",", ".").replace("\xa0", "")
        cleaned = re.sub(r"[^\d.-]", "", cleaned)
        return cleaned

    def _format_amount(self, amount: float) -> str:
        return f"{abs(amount):.2f}".replace(".", ",")

    def _format_date(self, date_str: str) -> str:
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%y%m%d")
        except (ValueError, TypeError):
            return ""

    def _wrap_text(self, text: str, length: int) -> List[str]:
        if not text:
            return []
        return [text[i : i + length] for i in range(0, len(text), length)]

    def convert(self, csv_content: str) -> str:
        lines = [line.strip() for line in csv_content.splitlines()]
        header_index = -1
        for i, line in enumerate(lines):
            if "#Data księgowania;" in line:
                header_index = i
                break

        if header_index == -1:
            raise ValueError("Nie znaleziono nagłówka transakcji w pliku CSV.")

        account_number = ""
        initial_balance = 0.0
        currency = "PLN"
        statement_date = ""

        for i, line in enumerate(lines[:header_index]):
            if "#Numer rachunku" in line:
                content = line
                if i + 1 < header_index and (len(line.split(";")) <= 1 or not line.split(";")[1].strip()):
                    content = lines[i + 1]
                match = re.search(r"(\d[\s\d]{20,})", content)
                if match:
                    account_number = re.sub(r"[^\d]", "", match.group(1))

            if "#Saldo początkowe" in line:
                content = line
                if i + 1 < header_index and (len(line.split(";")) <= 1 or not line.split(";")[1].strip()):
                    content = lines[i + 1]
                try:
                    parts = content.split(";")
                    val_str = self._clean_amount_str(parts[1] if len(parts) > 1 else parts[0])
                    initial_balance = float(val_str)
                except (IndexError, ValueError):
                    pass

        f = io.StringIO("\n".join(lines[header_index:]))
        reader = csv.DictReader(f, delimiter=";")
        
        # Przygotowanie transakcji do późniejszego użycia (potrzebujemy daty pierwszej transakcji)
        rows = []
        for row in reader:
            raw_date = row.get("#Data księgowania")
            if raw_date and re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
                rows.append(row)
        
        if rows and not statement_date:
            statement_date = self._format_date(rows[0]["#Data księgowania"])
        else:
            statement_date = datetime.datetime.now().strftime("%y%m%d")

        output = []
        # :20:
        output.append(":20:MT940")

        # :25:
        if account_number:
            output.append(f":25:/PL{account_number}")
        else:
            output.append(":25:/UNKNOWN_ACCOUNT")

        # :28C: Numer wyciągu (mBank używa daty YYMMDD)
        output.append(f":28C:{statement_date}")

        # :60F: Saldo początkowe
        sign_60 = "C" if initial_balance >= 0 else "D"
        output.append(f":60F:{sign_60}{statement_date}{currency}{self._format_amount(initial_balance)}")

        current_balance = initial_balance
        
        for idx, row in enumerate(rows):
            date_val = self._format_date(row["#Data księgowania"])
            amount = float(self._clean_amount_str(row.get("#Kwota", "0")))
            current_balance += amount

            # :61: Linia transakcji
            # Dodajemy numer referencyjny na końcu (np. SD95 + numer kolejny)
            sign_61 = "C" if amount >= 0 else "D"
            ref_num = f"{idx+1:011d}"
            output.append(f":61:{date_val}{date_val[2:]}{sign_61}{self._format_amount(amount)}SD95{ref_num}")

            # :86: Struktura mBanku (podwójny tag :86: i brak :86: w kolejnych liniach pola)
            output.append(":86:SD95")
            
            operation_type = row.get("#Opis operacji", "")
            title = row.get("#Tytuł", "")
            
            # Budujemy linię 2 pola 86
            details_line2 = f"SD95~00BD95{operation_type}"
            # Kolejne linie tytułu i danych
            details_remaining = []
            
            title_parts = self._wrap_text(title, 27)
            for i, part in enumerate(title_parts[:8]):
                details_remaining.append(f"~{20+i}{part}")
                
            contractor = row.get("#Nadawca/Odbiorca", "")
            contractor_parts = self._wrap_text(contractor, 35)
            if len(contractor_parts) > 0:
                details_remaining.append(f"~32{contractor_parts[0]}")
            if len(contractor_parts) > 1:
                details_remaining.append(f"~33{contractor_parts[1]}")
                
            acc = row.get("#Numer konta", "").replace("'", "").strip()
            if acc:
                acc_clean = re.sub(r"[^\d]", "", acc)
                if acc_clean:
                    details_remaining.append(f"~31{acc_clean}")
                    details_remaining.append(f"~38PL{acc_clean}")

            # Składamy wszystko w całość zgodnie z formatem mBanku
            # Pierwsza linia po :86: (druga w sumie)
            raw_full_86 = "".join(details_remaining)
            wrapped_86 = self._wrap_text(raw_full_86, 65)
            
            output.append(f":86:{details_line2}")
            for line in wrapped_86:
                output.append(line)

        # :62F:
        sign_62 = "C" if current_balance >= 0 else "D"
        # Data salda końcowego z ostatniej transakcji lub dzisiejsza
        last_date = self._format_date(rows[-1]["#Data księgowania"]) if rows else statement_date
        output.append(f":62F:{sign_62}{last_date}{currency}{self._format_amount(current_balance)}")

        # Dodajemy znak końca pliku (opcjonalnie, ale mBank często go nie ma, SWIFT wymaga tylko pól)
        # Łączymy używając CRLF
        return "\r\n".join(output) + "\r\n"
