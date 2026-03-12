from datetime import datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Account, AuditLog, Transaction
from .schemas import AccountCreate, AccountUpdate, TransactionCreate


def create_account(db: Session, payload: AccountCreate) -> Account:
    account = Account(name=payload.name, description=payload.description)
    db.add(account)
    db.commit()
    db.refresh(account)
    log_action(db, "account.create", "account", str(account.id), {"name": account.name})
    return account


def update_account(db: Session, account: Account, payload: AccountUpdate) -> Account:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(account, key, value)
    db.add(account)
    db.commit()
    db.refresh(account)
    log_action(db, "account.update", "account", str(account.id), data)
    return account


def list_accounts(db: Session) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.id)))


def get_account(db: Session, account_id: int) -> Optional[Account]:
    return db.get(Account, account_id)


def create_transaction(db: Session, payload: TransactionCreate) -> Transaction:
    transaction = Transaction(
        account_id=payload.account_id,
        type=payload.type.value,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    log_action(
        db,
        "transaction.create",
        "transaction",
        str(transaction.id),
        {"account_id": transaction.account_id, "amount": str(transaction.amount), "type": transaction.type},
    )
    return transaction


def list_transactions(
    db: Session,
    account_id: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[Transaction]:
    query = select(Transaction).order_by(Transaction.id.desc())
    if account_id is not None:
        query = query.where(Transaction.account_id == account_id)
    if start is not None:
        query = query.where(Transaction.created_at >= start)
    if end is not None:
        query = query.where(Transaction.created_at <= end)
    return list(db.scalars(query))


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.get(Transaction, transaction_id)


def report_summary(
    db: Session, start: Optional[datetime] = None, end: Optional[datetime] = None
) -> dict[str, Decimal]:
    query = select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0)).group_by(Transaction.type)
    if start is not None:
        query = query.where(Transaction.created_at >= start)
    if end is not None:
        query = query.where(Transaction.created_at <= end)
    rows = db.execute(query).all()
    totals = {"income": Decimal("0"), "expense": Decimal("0")}
    for txn_type, amount in rows:
        totals[txn_type] = Decimal(amount)
    net_total = totals["income"] - totals["expense"]
    return {
        "total_income": totals["income"],
        "total_expense": totals["expense"],
        "net_total": net_total,
    }


def report_by_account(
    db: Session, start: Optional[datetime] = None, end: Optional[datetime] = None
) -> list[dict[str, Decimal | int | str]]:
    query = (
        select(
            Account.id,
            Account.name,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .join(Transaction, Transaction.account_id == Account.id)
        .group_by(Account.id, Account.name, Transaction.type)
        .order_by(Account.id)
    )
    if start is not None:
        query = query.where(Transaction.created_at >= start)
    if end is not None:
        query = query.where(Transaction.created_at <= end)
    rows = db.execute(query).all()
    totals: dict[int, dict[str, Decimal | int | str]] = {}
    for account_id, account_name, txn_type, amount in rows:
        if account_id not in totals:
            totals[account_id] = {
                "account_id": account_id,
                "account_name": account_name,
                "total_income": Decimal("0"),
                "total_expense": Decimal("0"),
                "net_total": Decimal("0"),
            }
        if txn_type == "income":
            totals[account_id]["total_income"] = Decimal(amount)
        else:
            totals[account_id]["total_expense"] = Decimal(amount)
    for item in totals.values():
        item["net_total"] = Decimal(item["total_income"]) - Decimal(item["total_expense"])
    return list(totals.values())


def log_action(db: Session, action: str, entity_type: str, entity_id: str, details: Optional[dict] = None) -> AuditLog:
    entry = AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, details=details)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_audit_logs(db: Session, limit: int = 100) -> Iterable[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    return list(db.scalars(query))
