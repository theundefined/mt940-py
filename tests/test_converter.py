import pytest
from mt940_py.converter import MT940Converter

def test_clean_amount_str():
    conv = MT940Converter()
    assert conv._clean_amount_str("1 234,56 PLN") == "1234.56"
    assert conv._clean_amount_str("-75,82") == "-75.82"

def test_format_amount():
    conv = MT940Converter()
    assert conv._format_amount(1234.56) == "1234,56"

def test_format_date():
    conv = MT940Converter()
    assert conv._format_date("2026-01-10") == "260110"

def test_basic_conversion_structure():
    # Bardziej realistyczny format mBanku
    csv_content = (
        "#Numer rachunku;PL12345678901234567890123456;\n"
        "#Saldo początkowe;100,00 PLN;\n"
        "#Data księgowania;#Data operacji;#Opis operacji;#Tytuł;#Nadawca/Odbiorca;#Numer konta;#Kwota;#Saldo po operacji;\n"
        "2026-01-10;2026-01-10;OPIS;TYTUL;NADAWCA;112233;-10,00;90,00;\n"
    )
    conv = MT940Converter()
    result = conv.convert(csv_content)
    
    assert ":20:MT940" in result
    assert "/PL12345678901234567890123456" in result
    assert ":60F:C260110PLN100,00" in result
    assert "D10,00" in result
    assert ":62F:C260110PLN90,00" in result
    assert "\r\n" in result
    # Sprawdzenie podwójnego 86
    assert ":86:SD95\r\n:86:SD95~00BD95OPIS" in result
