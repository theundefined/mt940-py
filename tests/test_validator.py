import pytest
import os
from mt940_py.validator import MT940Validator
from mt940_py.converter import MT940Converter

def test_validator_success():
    csv_content = (
        "#Numer rachunku;1234567890\n"
        "#Saldo początkowe;100,00\n"
        "#Data księgowania;Tytuł;Kwota\n"
        "2026-01-10;TEST;50,00\n"
    )
    conv = MT940Converter()
    mt940_data = conv.convert(csv_content)
    
    temp_path = "tests/temp_test.txt"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(mt940_data)
    
    validator = MT940Validator()
    results = validator.validate_file(temp_path)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    assert results["is_valid"] is True

def test_validator_error():
    bad_mt940 = (
        ":20:MT940\r\n"
        ":25:/PL123\r\n"
        ":60F:C260101PLN100,00\r\n"
        ":61:2601010101C50,00SD95\r\n"
        ":86:TEST\r\n"
        ":62F:C260101PLN200,00\r\n"
    )
    temp_path = "tests/temp_bad.txt"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(bad_mt940)
        
    validator = MT940Validator()
    results = validator.validate_file(temp_path)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    assert results["is_valid"] is False
