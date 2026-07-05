# schema.py
from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    paid = "paid"
    unpaid = "unpaid"
    overdue = "overdue"
    partially_paid = "partially_paid"
    unknown = "unknown"


class Address(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None


class Party(BaseModel):
    name: str
    address: Address
    tax_id: Optional[str] = None
    email: Optional[str] = None


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: str = Field(description="ISO date string YYYY-MM-DD")
    due_date: Optional[str] = Field(default=None, description="ISO date string YYYY-MM-DD")
    status: InvoiceStatus
    vendor: Party
    buyer: Party
    line_items: List[LineItem]
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str = Field(description="Three-letter ISO currency code, e.g. USD")
    purchase_order_number: Optional[str] = None
    notes: Optional[str] = None