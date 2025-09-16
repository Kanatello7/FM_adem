from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import  Optional, Dict, Any


class TaskStatus(BaseModel):
    task_id: str
    state: str
    status: str
    meta: Optional[Dict[str, Any]] = None

class Report_3_22(BaseModel):
    name: str 
    bin_or_iin: str 

class Report_19_33_1(BaseModel):
    supporting_document: str
    supporting_document_date: datetime
    invoice_number: str
    invoice_date: datetime
    project: str
    responsible: str
    approver: str
    llc: str
    counterparty: str
    comment: str
    invoice_category: str
    bin_or_iin: str
    invoice_creator: str
    income_expense_item: str
    sales_orders: str
    iic: str
    agreement: str
    invoice_amount: Decimal
    previously_paid_amount: Decimal
    bank: str
    invoice_type: str
    subdivision: str
    document_number: str
    document_date: str
    status: str
    closing_document_provided_amount: Decimal
    currency: str

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
        }

class Report_19_20(BaseModel):
    number: str 
    status: str 

class Report_7_40(BaseModel):
    number: str 
    region: str 

class Report_bpartner_v(BaseModel):
    name: str 
    bin_or_iin: str 
    iic: str

