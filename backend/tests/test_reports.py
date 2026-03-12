from decimal import Decimal

from .conftest import get_test_client


def test_reports_summary_and_by_account() -> None:
    client = get_test_client()
    account = client.post("/accounts", json={"name": "Operations"})
    account_id = account.json()["id"]

    client.post(
        "/transactions",
        json={"account_id": account_id, "type": "income", "amount": "200.00", "currency": "USD"},
    )
    client.post(
        "/transactions",
        json={"account_id": account_id, "type": "expense", "amount": "50.00", "currency": "USD"},
    )

    summary = client.get("/reports/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert Decimal(data["total_income"]) >= Decimal("200.00")
    assert Decimal(data["total_expense"]) >= Decimal("50.00")

    by_account = client.get("/reports/by-account")
    assert by_account.status_code == 200
    items = by_account.json()
    assert any(item["account_id"] == account_id for item in items)
