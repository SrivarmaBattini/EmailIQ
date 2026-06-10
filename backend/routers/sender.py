from fastapi import APIRouter
from backend.db.supabase_client import get_sender_profile

router = APIRouter(prefix="/api", tags=["sender"])

@router.get("/sender/{sender_name}")
async def get_profile(sender_name: str):
    return get_sender_profile(sender_name)

@router.get("/senders")
async def list_senders():
    from backend.db.supabase_client import _memory_store
    return {"senders": list(_memory_store.keys())}
