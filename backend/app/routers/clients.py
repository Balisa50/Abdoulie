import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud
from app.database import get_db
from app.models import Client
from app.schemas import ClientCreate, ClientResponse, ClientUpdate
from app.security import verify_api_key
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/clients",
    tags=["clients"],
    dependencies=[Depends(verify_api_key)] if settings.require_api_key else [],
)


@router.post("", response_model=ClientResponse)
async def create_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Create a new client."""
    logger.info(f"Creating client: {client_in.email}")

    existing_client = await client_crud.get_by_email(db, client_in.email)
    if existing_client:
        raise HTTPException(status_code=400, detail="Client with this email already exists")

    client = await client_crud.create(db, client_in.model_dump())
    return ClientResponse.model_validate(client)


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[ClientResponse]:
    """List all clients."""
    logger.info(f"Listing clients: skip={skip}, limit={limit}")
    clients = await client_crud.get_all(db, skip=skip, limit=limit)
    return [ClientResponse.model_validate(client) for client in clients]


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Get a client by ID."""
    logger.info(f"Getting client: {client_id}")
    client = await client_crud.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientResponse.model_validate(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Update a client."""
    logger.info(f"Updating client: {client_id}")
    client = await client_crud.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client_in.model_dump(exclude_unset=True)
    updated_client = await client_crud.update(db, client, update_data)
    return ClientResponse.model_validate(updated_client)


@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete a client."""
    logger.info(f"Deleting client: {client_id}")
    client = await client_crud.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    await client_crud.delete(db, client_id)
    return {"status": "success", "message": "Client deleted"}
