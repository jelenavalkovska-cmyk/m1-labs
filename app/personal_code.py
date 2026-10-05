"""Personas koda pārbaude un normalizēšana (CR-1).

Noteikumi vienkāršoti mācību vajadzībām.
"""

import re
from datetime import date

from pydantic_core import PydanticCustomError

from app import config

_FORMAT = re.compile(r"\d{6}-?\d{5}")
_WEIGHTS = (1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
_CENTURIES = {"1": 1900, "2": 2000}
# No šī datuma dzimušajiem ir tikai jaunā formāta kodi (sākas ar 32).
_NEW_FORMAT_ONLY_FROM = date(2020, 1, 1)

# Esošie sintētiskie kodi (testi, sākuma dati, OMD imitācija), kuri neiztur
# kontrolciparu. Derīgi tikai ar ALLOW_TEST_PERSONAL_CODES=true.
TEST_CODES = frozenset(
    {
        "32000000001",
        "32000000002",
        "32000000101",
        "32000000102",
        "32000000103",
        "32000000404",
        "32000000408",
        "32000000500",
        "32000000503",
        "32000000999",
    }
)


def _check_digit_ok(digits: str) -> bool:
    total = sum(int(d) * w for d, w in zip(digits[:10], _WEIGHTS, strict=True))
    return (1101 - total) % 11 == int(digits[10])


def _birth_date(digits: str) -> date | None:
    century = _CENTURIES.get(digits[6])
    if century is None:
        return None
    try:
        return date(century + int(digits[4:6]), int(digits[2:4]), int(digits[0:2]))
    except ValueError:
        return None


def is_valid(digits: str) -> bool:
    """Pārbauda normalizētu kodu (11 cipari)."""
    if config.ALLOW_TEST_PERSONAL_CODES and digits in TEST_CODES:
        return True
    if not _check_digit_ok(digits):
        return False
    if digits.startswith("32"):
        return True
    born = _birth_date(digits)
    return born is not None and born <= date.today() and born < _NEW_FORMAT_ONLY_FROM


def validate(value: str) -> str:
    """Pydantic validators: atgriež kodu kā 11 ciparus bez defises un atstarpēm."""
    value = value.strip()
    if not value:
        raise PydanticCustomError("missing", "Field required")
    if not _FORMAT.fullmatch(value):
        raise PydanticCustomError("personal_code", "Invalid personal code")
    digits = value.replace("-", "")
    if not is_valid(digits):
        raise PydanticCustomError("personal_code", "Invalid personal code")
    return digits
