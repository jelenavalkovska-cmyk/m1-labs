"""CR-1: personas koda pārbaude iesniegumā."""

import pytest

from app import config


def post(client, payload, code):
    payload["personalCode"] = code
    return client.post("/submissions", json=payload)


def assert_rejected(response, issue="INVALID_FORMAT"):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]


@pytest.mark.parametrize("code", ["01019012349", "010190-12349"])
def test_cr1_ac1_old_format_valid(client, valid_payload, code):
    assert post(client, valid_payload, code).status_code == 201


@pytest.mark.parametrize("code", ["32123456785", "321234-56785"])
def test_cr1_ac2_new_format_valid(client, valid_payload, code):
    assert post(client, valid_payload, code).status_code == 201


def test_cr1_ac3_surrounding_spaces_trimmed(client, valid_payload):
    response = post(client, valid_payload, " 010190-12349 ")
    assert response.status_code == 201
    stored = client.get(f"/submissions/{response.json()['id']}").json()
    assert stored["personalCode"] == "01019012349"


@pytest.mark.parametrize("code", ["01019012340", "32123456780"])
def test_cr1_ac4_wrong_check_digit(client, valid_payload, code):
    assert_rejected(post(client, valid_payload, code))


def test_cr1_ac5_nonexistent_date(client, valid_payload):
    assert_rejected(post(client, valid_payload, "29020112341"))


def test_cr1_ac6_future_date(client, valid_payload):
    assert_rejected(post(client, valid_payload, "01013021236"))


@pytest.mark.parametrize(
    "code",
    [
        "01012521239",  # 01.01.2025, vecais formāts
        "01019001236",  # gadsimta cipars 0 (1800. gadi)
    ],
)
def test_cr1_ac7_born_2020_or_later_or_1800s(client, valid_payload, code):
    assert_rejected(post(client, valid_payload, code))


@pytest.mark.parametrize("code", ["0101901234", "01019O12349", "010190 12349"])
def test_cr1_ac8_wrong_length_or_characters(client, valid_payload, code):
    assert_rejected(post(client, valid_payload, code))


@pytest.mark.parametrize("code", [None, "", "   "])
def test_cr1_ac9_missing_or_blank_is_required(client, valid_payload, code):
    if code is None:
        del valid_payload["personalCode"]
        response = client.post("/submissions", json=valid_payload)
    else:
        response = post(client, valid_payload, code)
    assert_rejected(response, issue="REQUIRED")


def test_cr1_ac10_stored_and_sent_to_omd_normalised(client, valid_payload, fake_omd):
    response = post(client, valid_payload, "010190-12349")
    assert response.status_code == 201
    stored = client.get(f"/submissions/{response.json()['id']}").json()
    assert stored["personalCode"] == "01019012349"
    assert fake_omd.calls == ["01019012349"]


def test_cr1_ac11_test_code_allowed_when_enabled(client, valid_payload):
    assert post(client, valid_payload, "32000000001").status_code == 201


def test_cr1_ac12_test_code_rejected_by_default(client, valid_payload, monkeypatch):
    monkeypatch.setattr(config, "ALLOW_TEST_PERSONAL_CODES", False)
    assert_rejected(post(client, valid_payload, "32000000001"))


def test_cr1_ac13_unlisted_code_rejected_when_enabled(client, valid_payload):
    assert_rejected(post(client, valid_payload, "32000000003"))


def test_cr1_seed_readable_when_test_codes_disabled(client, monkeypatch):
    # Saglabātos kodus nepārbauda atkārtoti: GET nedrīkst krist ar 500.
    from app import storage

    monkeypatch.setattr(config, "ALLOW_TEST_PERSONAL_CODES", False)
    storage.reset()
    assert client.get("/submissions/IES-2026-000001").status_code == 200
