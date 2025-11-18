from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from schemas import Lead, LeadResponse

# Database helpers are pre-configured
from database import db, create_document, get_documents

app = FastAPI(
    title="CORPEX Informatics API",
    description="Backend for CORPEX Informatics website: leads, demo requests, and content endpoints.",
    version="1.0.0",
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "corpex-api"}


@app.get("/test", tags=["health"])
async def test_db():
    # Try a trivial query to ensure DB connectivity
    try:
        _ = await get_documents("lead", {}, limit=1)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LeadCreate(Lead):
    pass


@app.post("/leads", response_model=LeadResponse, tags=["leads"], summary="Create a lead/contact submission")
async def create_lead(payload: LeadCreate):
    data = payload.dict()
    data["created_at"] = datetime.utcnow()
    try:
        inserted = await create_document("lead", data)
        # create_document returns dict with `_id` and timestamps
        return LeadResponse(
            id=str(inserted.get("_id")),
            name=inserted["name"],
            email=inserted["email"],
            company=inserted.get("company"),
            phone=inserted.get("phone"),
            interest=inserted.get("interest"),
            created_at=inserted["created_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LeadsQuery(BaseModel):
    interest: Optional[str] = None
    limit: int = 50


@app.post("/leads/search", tags=["leads"], summary="Search leads (admin/debug)")
async def search_leads(query: LeadsQuery):
    filt = {}
    if query.interest:
        filt["interest"] = query.interest
    try:
        docs = await get_documents("lead", filt, limit=min(max(query.limit, 1), 200))
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
