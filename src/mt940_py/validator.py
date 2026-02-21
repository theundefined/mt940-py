import re
from typing import Dict, Any, List
import mt940  # type: ignore

class MT940Validator:
    """Walidator plików MT940 z uwzględnieniem polskich rozszerzeń ZBP."""

    def __init__(self) -> None:
        pass

    def parse_field_86(self, raw_details: str) -> Dict[str, str]:
        if not raw_details:
            return {}
        parts = re.split(r"~(\d{2})", raw_details)
        parsed: Dict[str, str] = {}
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                tag = parts[i]
                value = parts[i + 1].strip() if i + 1 < len(parts) else ""
                if tag in parsed:
                    parsed[tag] += " " + value
                else:
                    parsed[tag] = value
        return parsed

    def get_amount_value(self, obj: Any) -> float:
        if obj is None:
            return 0.0
        if hasattr(obj, "amount") and hasattr(obj.amount, "amount"):
            return float(obj.amount.amount)
        if hasattr(obj, "amount"):
            return float(obj.amount)
        try:
            return float(obj)
        except Exception:
            return 0.0

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "statements_count": 0,
            "transactions_count": 0,
        }

        try:
            data = mt940.parse(file_path)

            if hasattr(data, "data"):
                statements = [data]
            else:
                statements = data

            results["statements_count"] = len(statements)

            for statement in statements:
                opening = statement.data.get("final_opening_balance")
                closing = statement.data.get("final_closing_balance")

                initial_val = self.get_amount_value(opening)
                expected_final = self.get_amount_value(closing)

                actual_sum = initial_val

                for transaction in statement:
                    results["transactions_count"] += 1
                    amount = transaction.data.get("amount")
                    actual_sum += self.get_amount_value(amount)

                    raw_86 = transaction.data.get("transaction_details", "")
                    self.parse_field_86(raw_86)

                if abs(actual_sum - expected_final) > 0.01:
                    results["is_valid"] = False
                    results["errors"].append(
                        f"Błąd sumy kontrolnej: Saldo pocz. ({initial_val:.2f}) + transakcje = {actual_sum:.2f}, "
                        f"a saldo końcowe w pliku to {expected_final:.2f}"
                    )

        except Exception as e:
            results["is_valid"] = False
            results["errors"].append(f"Błąd krytyczny parsowania: {str(e)}")

        return results
