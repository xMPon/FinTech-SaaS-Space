from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class AccountOut(AccountBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    account_id: int
    type: TransactionType
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    description: Optional[str] = Field(default=None, max_length=500)


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    details: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportSummaryOut(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_total: Decimal


class ReportByAccountOut(BaseModel):
    account_id: int
    account_name: str
    total_income: Decimal
    total_expense: Decimal
    net_total: Decimal
