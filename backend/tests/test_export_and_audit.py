from .conftest import get_test_client


def test_export_transactions_csv_and_audit_logs() -> None:
    client = get_test_client()
    account = client.post("/accounts", json={"name": "Export Account"})
    account_id = account.json()["id"]

    client.post(
        "/transactions",
        json={"account_id": account_id, "type": "income", "amount": "10.00", "currency": "USD"},
    )

    export = client.get("/export/transactions.csv")
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
    assert "transactions.csv" in export.headers["content-disposition"]
    assert "account_id" in export.text

    audit = client.get("/audit-logs")
    assert audit.status_code == 200
    assert len(audit.json()) >= 2
