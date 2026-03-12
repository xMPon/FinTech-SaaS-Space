from datetime import datetime
from hmac import compare_digest
from io import StringIO
import csv

from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from .crud import (
    create_account,
    create_transaction,
    get_account,
    get_transaction,
    list_accounts,
    list_audit_logs,
    list_transactions,
    report_by_account,
    report_summary,
    update_account,
)
from .db import Base, engine, get_db
from .schemas import (
    AccountCreate,
    AccountOut,
    AccountUpdate,
    AuditLogOut,
    ReportByAccountOut,
    ReportSummaryOut,
    TransactionCreate,
    TransactionOut,
)
from .settings import settings


app = FastAPI(title=settings.app_name)

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)


def require_admin_token(api_key: str | None = Security(api_key_header)) -> None:
    if not api_key or not compare_digest(api_key, settings.admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def landing_page() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>FinTech SaaS Space MVP</title>
        <style>
          :root {
            color-scheme: light;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
          }
          body {
            margin: 0;
            background: #0f1b2d;
            color: #f5f7fb;
          }
          .wrap {
            max-width: 900px;
            margin: 0 auto;
            padding: 48px 24px 64px;
          }
          .card {
            background: #17263d;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
          }
          h1 {
            margin: 0 0 12px;
            font-size: 2.2rem;
            letter-spacing: 0.5px;
          }
          p {
            margin: 0 0 18px;
            line-height: 1.6;
            color: #d6deea;
          }
          code {
            background: #0c1424;
            padding: 2px 6px;
            border-radius: 6px;
            color: #ffd479;
          }
          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 20px;
          }
          a {
            color: #0f1b2d;
            background: #7bdff2;
            text-decoration: none;
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600;
          }
          .secondary {
            background: #f6ae2d;
          }
          .note {
            margin-top: 24px;
            font-size: 0.9rem;
            color: #b8c4d6;
          }
          .panel {
            margin-top: 28px;
            background: #0c1424;
            border-radius: 12px;
            padding: 20px;
          }
          label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
          }
          input, select, button {
            width: 100%;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #24324a;
            background: #0f1b2d;
            color: #f5f7fb;
            font-size: 0.95rem;
          }
          button {
            background: #7bdff2;
            color: #0f1b2d;
            font-weight: 700;
            cursor: pointer;
            border: none;
          }
          button.secondary {
            background: #f6ae2d;
          }
          .grid {
            display: grid;
            gap: 16px;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          }
          .result {
            margin-top: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            background: #141f33;
            color: #d6deea;
            font-size: 0.9rem;
            max-height: 180px;
            overflow: auto;
          }
          .error {
            color: #ffb3b3;
          }
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="card">
            <h1>FinTech SaaS Space MVP</h1>
            <p>
              This is a local-first, API-only proof of concept for a simple
              financial ledger and analytics platform.
            </p>
            <p>
              Use the admin token header <code>X-Admin-Token</code> to access
              API endpoints.
            </p>
            <div class="actions">
              <a href="/docs">Open API Docs</a>
              <a class="secondary" href="/health">Health Check</a>
            </div>
            <div class="panel">
              <div class="grid">
                <div>
                  <label for="token">Admin token</label>
                  <input id="token" type="password" placeholder="Enter X-Admin-Token" />
                  <button style="margin-top:10px" onclick="saveToken()">Save Token</button>
                </div>
                <div>
                  <label for="accountName">New account name</label>
                  <input id="accountName" type="text" placeholder="e.g. Operating Account" />
                  <label for="accountDesc" style="margin-top:10px">Description</label>
                  <input id="accountDesc" type="text" placeholder="Optional" />
                  <button style="margin-top:10px" onclick="createAccount()">Create Account</button>
                </div>
                <div>
                  <label for="transactionAccount">Transaction account</label>
                  <select id="transactionAccount"></select>
                  <label for="transactionType" style="margin-top:10px">Type</label>
                  <select id="transactionType">
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                  <label for="transactionAmount" style="margin-top:10px">Amount</label>
                  <input id="transactionAmount" type="number" step="0.01" placeholder="0.00" />
                  <button class="secondary" style="margin-top:10px" onclick="createTransaction()">Add Transaction</button>
                </div>
              </div>
              <div class="grid" style="margin-top:16px">
                <div>
                  <button onclick="loadAccounts()">Refresh Accounts</button>
                  <div id="accountsResult" class="result"></div>
                </div>
                <div>
                  <button onclick="loadSummary()">Load Summary</button>
                  <div id="summaryResult" class="result"></div>
                </div>
                <div>
                  <button onclick="loadTransactions()">Recent Transactions</button>
                  <div id="transactionsResult" class="result"></div>
                </div>
              </div>
            </div>
            <p class="note">
              Security reminder: this MVP is intended for local use only.
            </p>
          </div>
        </div>
        <script>
          const tokenInput = document.getElementById("token");
          const accountSelect = document.getElementById("transactionAccount");
          const accountsResult = document.getElementById("accountsResult");
          const summaryResult = document.getElementById("summaryResult");
          const transactionsResult = document.getElementById("transactionsResult");

          const storedToken = localStorage.getItem("adminToken");
          if (storedToken) {
            tokenInput.value = storedToken;
          }

          function getHeaders() {
            const token = tokenInput.value.trim();
            return {
              "Content-Type": "application/json",
              "X-Admin-Token": token,
            };
          }

          function showResult(el, data, isError = false) {
            el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
            el.classList.toggle("error", isError);
          }

          function saveToken() {
            const token = tokenInput.value.trim();
            if (!token) {
              alert("Please enter a token.");
              return;
            }
            localStorage.setItem("adminToken", token);
            alert("Token saved locally.");
          }

          async function loadAccounts() {
            try {
              const response = await fetch("/accounts", { headers: getHeaders() });
              if (!response.ok) throw new Error("Unauthorized or failed request.");
              const data = await response.json();
              showResult(accountsResult, data);
              accountSelect.innerHTML = "";
              data.forEach((acct) => {
                const option = document.createElement("option");
                option.value = acct.id;
                option.textContent = `${acct.name} (id ${acct.id})`;
                accountSelect.appendChild(option);
              });
            } catch (err) {
              showResult(accountsResult, err.message, true);
            }
          }

          async function createAccount() {
            const name = document.getElementById("accountName").value.trim();
            const description = document.getElementById("accountDesc").value.trim();
            if (!name) {
              alert("Account name is required.");
              return;
            }
            try {
              const response = await fetch("/accounts", {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({ name, description: description || null }),
              });
              if (!response.ok) throw new Error("Failed to create account.");
              await loadAccounts();
            } catch (err) {
              showResult(accountsResult, err.message, true);
            }
          }

          async function createTransaction() {
            const accountId = parseInt(accountSelect.value, 10);
            const type = document.getElementById("transactionType").value;
            const amount = document.getElementById("transactionAmount").value;
            if (!accountId || !amount) {
              alert("Select an account and enter an amount.");
              return;
            }
            try {
              const response = await fetch("/transactions", {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({
                  account_id: accountId,
                  type,
                  amount,
                  currency: "USD",
                }),
              });
              if (!response.ok) throw new Error("Failed to create transaction.");
              await loadTransactions();
              await loadSummary();
            } catch (err) {
              showResult(transactionsResult, err.message, true);
            }
          }

          async function loadSummary() {
            try {
              const response = await fetch("/reports/summary", { headers: getHeaders() });
              if (!response.ok) throw new Error("Failed to load summary.");
              const data = await response.json();
              showResult(summaryResult, data);
            } catch (err) {
              showResult(summaryResult, err.message, true);
            }
          }

          async function loadTransactions() {
            try {
              const response = await fetch("/transactions", { headers: getHeaders() });
              if (!response.ok) throw new Error("Failed to load transactions.");
              const data = await response.json();
              showResult(transactionsResult, data);
            } catch (err) {
              showResult(transactionsResult, err.message, true);
            }
          }

          loadAccounts();
        </script>
      </body>
    </html>
    """


@app.get("/accounts", response_model=list[AccountOut], dependencies=[Depends(require_admin_token)])
def get_accounts(db: Session = Depends(get_db)) -> list[AccountOut]:
    return list_accounts(db)


@app.post("/accounts", response_model=AccountOut, status_code=201, dependencies=[Depends(require_admin_token)])
def post_account(payload: AccountCreate, db: Session = Depends(get_db)) -> AccountOut:
    return create_account(db, payload)


@app.patch("/accounts/{account_id}", response_model=AccountOut, dependencies=[Depends(require_admin_token)])
def patch_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)) -> AccountOut:
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return update_account(db, account, payload)


@app.get("/transactions", response_model=list[TransactionOut], dependencies=[Depends(require_admin_token)])
def get_transactions(
    account_id: int | None = None,
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[TransactionOut]:
    return list_transactions(db, account_id=account_id, start=start, end=end)


@app.post("/transactions", response_model=TransactionOut, status_code=201, dependencies=[Depends(require_admin_token)])
def post_transaction(payload: TransactionCreate, db: Session = Depends(get_db)) -> TransactionOut:
    account = get_account(db, payload.account_id)
    if not account or not account.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive or missing")
    return create_transaction(db, payload)


@app.get(
    "/transactions/{transaction_id}",
    response_model=TransactionOut,
    dependencies=[Depends(require_admin_token)],
)
def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)) -> TransactionOut:
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/reports/summary", response_model=ReportSummaryOut, dependencies=[Depends(require_admin_token)])
def get_report_summary(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ReportSummaryOut:
    return report_summary(db, start=start, end=end)


@app.get(
    "/reports/by-account",
    response_model=list[ReportByAccountOut],
    dependencies=[Depends(require_admin_token)],
)
def get_report_by_account(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ReportByAccountOut]:
    return report_by_account(db, start=start, end=end)


@app.get("/export/transactions.csv", dependencies=[Depends(require_admin_token)])
def export_transactions(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    rows = list_transactions(db, start=start, end=end)
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "account_id", "type", "amount", "currency", "description", "created_at"])
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.account_id,
                row.type,
                row.amount,
                row.currency,
                row.description or "",
                row.created_at.isoformat(),
            ]
        )
    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=transactions.csv"}
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)


@app.get("/audit-logs", response_model=list[AuditLogOut], dependencies=[Depends(require_admin_token)])
def get_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AuditLogOut]:
    return list_audit_logs(db, limit=limit)
