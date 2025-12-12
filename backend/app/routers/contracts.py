"""Contracts router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import contract_crud
from app.database import get_db
from app.schemas import ContractCreate, ContractResponse, ContractUpdate

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractResponse])
async def list_contracts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all contracts."""
    return await contract_crud.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(contract: ContractCreate, db: AsyncSession = Depends(get_db)):
    """Create a new contract."""
    return await contract_crud.create(db, contract.model_dump())


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get contract by ID."""
    db_contract = await contract_crud.get(db, contract_id)
    if not db_contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return db_contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: UUID, contract: ContractUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a contract."""
    db_contract = await contract_crud.get(db, contract_id)
    if not db_contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return await contract_crud.update(db, db_contract, contract.model_dump(exclude_unset=True))


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a contract."""
    db_contract = await contract_crud.get(db, contract_id)
    if not db_contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    await contract_crud.delete(db, contract_id)


@router.get("/search/client/{client_id}", response_model=list[ContractResponse])
async def list_client_contracts(
    client_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all contracts for a specific client."""
    return await contract_crud.get_by_client_id(db, client_id, skip=skip, limit=limit)
