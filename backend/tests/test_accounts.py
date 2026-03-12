from .conftest import get_test_client


def test_create_and_list_accounts() -> None:
    client = get_test_client()
    payload = {"name": "Primary Account", "description": "Main ledger"}
    response = client.post("/accounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Primary Account"
    assert data["is_active"] is True

    list_response = client.get("/accounts")
    assert list_response.status_code == 200
    items = list_response.json()
    assert any(item["name"] == "Primary Account" for item in items)


def test_update_account() -> None:
    client = get_test_client()
    response = client.post("/accounts", json={"name": "To Update"})
    account_id = response.json()["id"]

    patch = client.patch(f"/accounts/{account_id}", json={"name": "Updated", "is_active": False})
    assert patch.status_code == 200
    updated = patch.json()
    assert updated["name"] == "Updated"
    assert updated["is_active"] is False
