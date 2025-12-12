"""Clients router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud
from app.database import get_db
from app.schemas import ClientCreate, ClientResponse, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientResponse])
async def list_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all clients."""
    return await client_crud.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    """Create a new client."""
    return await client_crud.create(db, client.model_dump())


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get client by ID."""
    db_client = await client_crud.get(db, client_id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID, client: ClientUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a client."""
    db_client = await client_crud.get(db, client_id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return await client_crud.update(db, db_client, client.model_dump(exclude_unset=True))


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a client."""
    db_client = await client_crud.get(db, client_id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    await client_crud.delete(db, client_id)
