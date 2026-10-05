"""CR-1: personas koda pārbaude iesniegumā (tikai formāts)."""

import logging

import pytest


def post(client, payload, code):
    payload["personalCode"] = code
    return client.post("/submissions", json=payload)


def assert_rejected(response, issue):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]


def stored_code(client, response):
    return client.get(f"/submissions/{response.json()['id']}").json()["personalCode"]


def test_cr1_ac1_eleven_digits(client, valid_payload):
    response = post(client, valid_payload, "32000000001")
    assert response.status_code == 201
    assert stored_code(client, response) == "32000000001"


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    response = post(client, valid_payload, "320000-00001")
    assert response.status_code == 201
    assert stored_code(client, response) == "32000000001"


def test_cr1_ac3_spaces_trimmed(client, valid_payload):
    response = post(client, valid_payload, " 32000000001 ")
    assert response.status_code == 201
    assert stored_code(client, response) == "32000000001"


def test_cr1_ac4_ten_digits(client, valid_payload):
    assert_rejected(post(client, valid_payload, "3200000000"), "INVALID_FORMAT")


def test_cr1_ac5_twelve_digits(client, valid_payload):
    assert_rejected(post(client, valid_payload, "320000000012"), "INVALID_FORMAT")


def test_cr1_ac6_letter_o(client, valid_payload):
    assert_rejected(post(client, valid_payload, "32000000O01"), "INVALID_FORMAT")


def test_cr1_ac7_missing_field(client, valid_payload):
    del valid_payload["personalCode"]
    assert_rejected(client.post("/submissions", json=valid_payload), "REQUIRED")


@pytest.mark.parametrize("code", ["", "   "])
def test_cr1_ac7_blank_is_required(client, valid_payload, code):
    # Precizējums: tukša virkne vai tikai atstarpes = REQUIRED
    assert_rejected(post(client, valid_payload, code), "REQUIRED")


def test_cr1_ac8_old_format_with_hyphen(client, valid_payload):
    response = post(client, valid_payload, "311299-21233")
    assert response.status_code == 201
    assert stored_code(client, response) == "31129921233"


def test_cr1_ac9_hyphen_in_wrong_place(client, valid_payload):
    assert_rejected(post(client, valid_payload, "3200-0000001"), "INVALID_FORMAT")


def test_cr1_invalid_code_not_echoed(client, valid_payload, caplog):
    # Precizējums: ievadīto kodu neatkārto ne atbildē, ne žurnālā
    code = "3200-0000001"
    with caplog.at_level(logging.DEBUG):
        response = post(client, valid_payload, code)
    assert response.status_code == 400
    assert code not in response.text
    assert code not in caplog.text
