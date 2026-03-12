from datetime import datetime
from io import StringIO
import csv

from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.responses import StreamingResponse
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
    if api_key != settings.admin_token:
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
