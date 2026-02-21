import csv
import datetime
import io
import re
from typing import List

class MT940Converter:
    """Konwerter plików CSV (mBank) do formatu MT940 (ZBP)."""

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

        output = []
        output.append(":20:MT940")

        if account_number:
            output.append(f":25:/PL{account_number}")
        else:
            output.append(":25:/UNKNOWN_ACCOUNT")

        output.append(":28C:00001")

        today_swift = datetime.datetime.now().strftime("%y%m%d")
        output.append(f":60F:C{today_swift}{currency}{self._format_amount(initial_balance)}")

        current_balance = initial_balance

        for row in reader:
            raw_date = row.get("#Data księgowania")
            if not raw_date or not re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
                continue

            date_val = self._format_date(raw_date)
            try:
                amount_str = self._clean_amount_str(row.get("#Kwota", "0"))
                amount = float(amount_str)
            except (ValueError, TypeError):
                continue

            current_balance += amount

            sign_61 = "C" if amount >= 0 else "D"
            output.append(f":61:{date_val}{date_val[2:]}{sign_61}{self._format_amount(amount)}SD95")

            details = []
            details.append("~00BD95")

            operation_type = row.get("#Opis operacji", "")
            title = row.get("#Tytuł", "")
            full_title = f"{operation_type} {title}".strip()

            for i, part in enumerate(self._wrap_text(full_title, 27)[:8]):
                details.append(f"~{20+i}{part}")

            contractor = row.get("#Nadawca/Odbiorca", "")
            contractor_parts = self._wrap_text(contractor, 35)
            if len(contractor_parts) > 0:
                details.append(f"~32{contractor_parts[0]}")
            if len(contractor_parts) > 1:
                details.append(f"~33{contractor_parts[1]}")

            acc = row.get("#Numer konta", "").replace("'", "").strip()
            if acc:
                acc_clean = re.sub(r"[^\d]", "", acc)
                if acc_clean:
                    details.append(f"~31{acc_clean}")
                    details.append(f"~38PL{acc_clean}")

            raw_86 = "".join(details)
            formatted_86 = self._wrap_text(raw_86, 65)
            if formatted_86:
                output.append(f":86:{formatted_86[0]}")
                for extra_line in formatted_86[1:]:
                    output.append(extra_line)

        output.append(f":62F:C{today_swift}{currency}{self._format_amount(current_balance)}")

        return "\n".join(output)
