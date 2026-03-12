from decimal import Decimal

from .conftest import get_test_client


def test_create_transaction_requires_active_account() -> None:
    client = get_test_client()
    account = client.post("/accounts", json={"name": "Inactive"})
    account_id = account.json()["id"]
    client.patch(f"/accounts/{account_id}", json={"is_active": False})

    response = client.post(
        "/transactions",
        json={"account_id": account_id, "type": "income", "amount": "10.00", "currency": "USD"},
    )
    assert response.status_code == 400


def test_create_and_get_transaction() -> None:
    client = get_test_client()
    account = client.post("/accounts", json={"name": "Revenue"})
    account_id = account.json()["id"]

    create = client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "type": "income",
            "amount": "125.50",
            "currency": "USD",
            "description": "Invoice payment",
        },
    )
    assert create.status_code == 201
    created = create.json()
    assert created["amount"] == "125.50"

    fetched = client.get(f"/transactions/{created['id']}")
    assert fetched.status_code == 200
    assert Decimal(fetched.json()["amount"]) == Decimal("125.50")
