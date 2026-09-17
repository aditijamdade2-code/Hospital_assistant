from typing import List
from fastapi import APIRouter, HTTPException
from backend.app.protocols.loader import protocol_loader
from backend.app.schemas.protocol import ProtocolSchema

router = APIRouter(prefix="/protocols", tags=["Protocols"])

@router.get("", response_model=List[ProtocolSchema])
async def list_protocols():
    """Lists all available clinical protocols."""
    return protocol_loader.list_all()

@router.get("/{protocol_id}", response_model=ProtocolSchema)
async def get_protocol(protocol_id: str):
    """Retrieves a single protocol by its ID."""
    proto = protocol_loader.get(protocol_id)
    if not proto:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return proto
