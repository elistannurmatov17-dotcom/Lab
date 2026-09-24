import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

import pytest
from pydantic import ValidationError
from app.schemas import ApplicationCreate

VALID = {
    "login": "client@example.com",
    "password": "secret",
    "inn": "12345678901234",
    "company": "ИП Тест",
    "legal_address": "Бишкек, ул. Тестовая, 1",
    "director": "Иванов Иван Иванович",
    "director_inn": "43210987654321",
    "director_phone": "+996 500 123 456",
    "director_email": "test@example.com",
    "extra_phone": "+996 700 123 456",
    "extra_name": "Петр",
    "object_type": "Магазин",
    "activity": "Розничная торговля одеждой",
    "ugns": "Октябрьский",
    "place_type": "Стационарная точка",
    "point_name": "Магазин",
    "point_address": "Бишкек, ул. Тестовая, 1",
    "tax_regime": "Общий налоговый режим",
    "vat": False,
    "calc_types": ["1. Товар"],
    "comment": None,
}

def test_valid_application():
    a = ApplicationCreate(**VALID)
    assert a.inn == "12345678901234"
    assert a.calc_types == ["1. Товар"]

def test_bad_inn():
    data = {**VALID, "inn": "123"}
    with pytest.raises(ValidationError):
        ApplicationCreate(**data)

def test_bad_phone():
    data = {**VALID, "director_phone": "0500123456"}
    with pytest.raises(ValidationError):
        ApplicationCreate(**data)
