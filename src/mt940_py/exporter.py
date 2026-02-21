import csv
import io
import re
import mt940
from mt940_py.validator import MT940Validator


class MT940ToCSVExporter:
    """Eksporter plików MT940 do formatu CSV."""

    def __init__(self) -> None:
        self.validator = MT940Validator()

    def _clean_text(self, text: str) -> str:
        """Usuwa znaki nowej linii i nadmiarowe spacje."""
        if not text:
            return ""
        # Zamieniamy nową linię na spację
        cleaned = text.replace("\n", " ").replace("\r", " ")
        # Usuwamy wielokrotne spacje
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def export(self, mt940_path: str) -> str:
        statements = mt940.parse(mt940_path)

        output = io.StringIO()
        fieldnames = [
            "Data księgowania",
            "Kwota",
            "Waluta",
            "Typ",
            "Kontrahent",
            "Rachunek kontrahenta",
            "Tytuł",
            "Szczegóły RAW",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        if hasattr(statements, "data"):
            statements_list = [statements]
        else:
            statements_list = statements

        for statement in statements_list:
            for transaction in statement:
                data = transaction.data
                raw_86 = data.get("transaction_details", "")
                parsed_86 = self.validator.parse_field_86(raw_86)

                title_parts = []
                for i in range(20, 28):
                    val = parsed_86.get(str(i))
                    if val:
                        title_parts.append(val)

                contractor = f"{parsed_86.get('32', '')} {parsed_86.get('33', '')}".strip()
                acc = parsed_86.get("31", parsed_86.get("38", ""))

                amount = self.validator.get_amount_value(data.get("amount"))

                writer.writerow(
                    {
                        "Data księgowania": data.get("date"),
                        "Kwota": f"{amount:.2f}",
                        "Waluta": data.get("currency"),
                        "Typ": data.get("status"),
                        "Kontrahent": self._clean_text(contractor),
                        "Rachunek kontrahenta": self._clean_text(acc),
                        "Tytuł": self._clean_text(" ".join(title_parts)),
                        "Szczegóły RAW": self._clean_text(raw_86),
                    }
                )

        return output.getvalue()
