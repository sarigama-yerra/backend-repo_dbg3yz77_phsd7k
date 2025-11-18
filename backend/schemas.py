from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class Lead(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=120)
    phone: Optional[str] = Field(None, max_length=40)
    message: Optional[str] = Field(None, max_length=2000)
    interest: Optional[str] = Field(
        None,
        description="Area of interest such as QMS, LIMS, ERP, CRM, Data Integration, CSV, etc.",
        max_length=80,
    )
    source: Optional[str] = Field(
        "website",
        description="Submission source, defaults to website",
        max_length=50,
    )
    created_at: Optional[datetime] = None


class LeadResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    company: Optional[str]
    phone: Optional[str]
    interest: Optional[str]
    created_at: datetime
