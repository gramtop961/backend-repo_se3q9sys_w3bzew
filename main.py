import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import User, Cat, Sighting, Place, Post, Emergency, Report, Badge, Article

app = FastAPI(title="CatAdvisor API", version="0.1.0", description="MVP backend for CatAdvisor: social + map for urban cats")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Helpers --------------------

def collection_name(model_cls) -> str:
    return model_cls.__name__.lower()


def to_public(doc: Dict[str, Any]):
    if not doc:
        return doc
    # Convert Mongo ObjectId if present
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


# -------------------- Health --------------------

@app.get("/")
def root():
    return {"name": "CatAdvisor API", "status": "ok"}


@app.get("/test")
def test_database():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            resp["database"] = "✅ Available"
            resp["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            resp["database_name"] = os.getenv("DATABASE_NAME", "❌ Not Set") or "❌ Not Set"
            resp["connection_status"] = "Connected"
            try:
                resp["collections"] = db.list_collection_names()
                resp["database"] = "✅ Connected & Working"
            except Exception as e:
                resp["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"
    return resp


# -------------------- Auth (MVP placeholder) --------------------
# For MVP: email-only pseudo auth (no OAuth yet). In real app we'd integrate OAuth providers.

class SignupPayload(BaseModel):
    email: str
    nickname: str
    avatar_url: Optional[str] = None


@app.post("/auth/signup")
def signup(payload: SignupPayload):
    data = User(
        email=payload.email,
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
        bio=None,
        role="user",
        points=0,
        badges=[],
        is_active=True,
    )
    uid = create_document(collection_name(User), data)
    return {"id": uid}


# -------------------- Map & Content Endpoints --------------------

@app.post("/cats")
def create_cat(cat: Cat):
    cid = create_document(collection_name(Cat), cat)
    return {"id": cid}


@app.get("/cats")
def list_cats(q: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    filt: Dict[str, Any] = {}
    if q:
        # very simple text filter on name/description
        filt = {"$or": [{"name": {"$regex": q, "$options": "i"}}, {"description": {"$regex": q, "$options": "i"}}]}
    docs = get_documents(collection_name(Cat), filt, limit)
    return [to_public(d) for d in docs]


@app.post("/sightings")
def create_sighting(s: Sighting):
    sid = create_document(collection_name(Sighting), s)
    return {"id": sid}


@app.get("/sightings")
def list_sightings(
    ne_lat: Optional[float] = None,
    ne_lng: Optional[float] = None,
    sw_lat: Optional[float] = None,
    sw_lng: Optional[float] = None,
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
):
    filt: Dict[str, Any] = {}
    if status:
        filt["status"] = status
    # Simple bbox filter if all corners present
    if None not in (ne_lat, ne_lng, sw_lat, sw_lng):
        filt.update({
            "lat": {"$gte": min(sw_lat, ne_lat), "$lte": max(sw_lat, ne_lat)},
            "lng": {"$gte": min(sw_lng, ne_lng), "$lte": max(sw_lng, ne_lng)},
        })
    docs = get_documents(collection_name(Sighting), filt, limit)
    return [to_public(d) for d in docs]


@app.post("/places")
def create_place(p: Place):
    pid = create_document(collection_name(Place), p)
    return {"id": pid}


@app.get("/places")
def list_places(
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=300)
):
    filt: Dict[str, Any] = {}
    if category:
        filt["category"] = category
    docs = get_documents(collection_name(Place), filt, limit)
    return [to_public(d) for d in docs]


@app.post("/posts")
def create_post(p: Post):
    pid = create_document(collection_name(Post), p)
    return {"id": pid}


@app.get("/posts")
def list_posts(limit: int = Query(50, ge=1, le=200)):
    docs = get_documents(collection_name(Post), {}, limit)
    return [to_public(d) for d in docs]


@app.post("/emergencies")
def create_emergency(e: Emergency):
    eid = create_document(collection_name(Emergency), e)
    return {"id": eid}


@app.get("/emergencies")
def list_emergencies(status: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    filt: Dict[str, Any] = {}
    if status:
        filt["status"] = status
    docs = get_documents(collection_name(Emergency), filt, limit)
    return [to_public(d) for d in docs]


@app.post("/reports")
def create_report(r: Report):
    rid = create_document(collection_name(Report), r)
    return {"id": rid}


@app.get("/badges")
def list_badges(limit: int = Query(100, ge=1, le=500)):
    docs = get_documents(collection_name(Badge), {}, limit)
    return [to_public(d) for d in docs]


@app.post("/badges")
def create_badge(b: Badge):
    bid = create_document(collection_name(Badge), b)
    return {"id": bid}


@app.get("/articles")
def list_articles(limit: int = Query(50, ge=1, le=200)):
    docs = get_documents(collection_name(Article), {}, limit)
    return [to_public(d) for d in docs]


@app.post("/articles")
def create_article(a: Article):
    aid = create_document(collection_name(Article), a)
    return {"id": aid}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
