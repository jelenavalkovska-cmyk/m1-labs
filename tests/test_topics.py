"""CR-0: tēma "Parki un skvēri" un tēmu saraksts."""

EXPECTED_TOPICS = [
    {"code": "ROADS", "name": "Ceļi un ielas"},
    {"code": "WASTE", "name": "Atkritumi"},
    {"code": "PLANNING", "name": "Teritorijas plānošana"},
    {"code": "PARKS", "name": "Parki un skvēri"},
    {"code": "OTHER", "name": "Cits"},
]


def test_list_topics_returns_contract_list_in_order(client):
    # AC1, AC4: precīzs saraksts un secība, OTHER beigās
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == EXPECTED_TOPICS


def test_parks_topic_is_accepted(client, valid_payload):
    # AC2
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    stored = client.get(f"/submissions/{response.json()['id']}").json()
    assert stored["topic"] == "PARKS"


def test_unknown_topic_returns_validation_error(client, valid_payload):
    # AC3
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "topic", "issue": "INVALID_FORMAT"} in error["details"]


def test_every_listed_topic_is_accepted(client, valid_payload):
    # Saraksts un validācija nāk no viena avota
    for topic in client.get("/topics").json():
        valid_payload["topic"] = topic["code"]
        assert client.post("/submissions", json=valid_payload).status_code == 201
