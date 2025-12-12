import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud, contract_crud
from app.database import get_db
from app.schemas import ContractCreate, ContractResponse, ContractUpdate
from app.security import verify_api_key
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/contracts",
    tags=["contracts"],
    dependencies=[Depends(verify_api_key)] if settings.require_api_key else [],
)


@router.post("", response_model=ContractResponse)
async def create_contract(
    contract_in: ContractCreate,
    db: AsyncSession = Depends(get_db),
) -> ContractResponse:
    """Create a new contract."""
    logger.info(f"Creating contract: {contract_in.contract_number} for client {contract_in.client_id}")

    client = await client_crud.get(db, contract_in.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    existing_contract = await contract_crud.get_by_contract_number(db, contract_in.contract_number)
    if existing_contract:
        raise HTTPException(status_code=400, detail="Contract with this number already exists")

    contract = await contract_crud.create(db, contract_in.model_dump())
    return ContractResponse.model_validate(contract)


@router.get("", response_model=list[ContractResponse])
async def list_contracts(
    client_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[ContractResponse]:
    """List contracts, optionally filtered by client."""
    logger.info(f"Listing contracts: client_id={client_id}, skip={skip}, limit={limit}")

    if client_id:
        client = await client_crud.get(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        contracts = await contract_crud.get_by_client_id(db, client_id, skip=skip, limit=limit)
    else:
        contracts = await contract_crud.get_all(db, skip=skip, limit=limit)

    return [ContractResponse.model_validate(contract) for contract in contracts]


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ContractResponse:
    """Get a contract by ID."""
    logger.info(f"Getting contract: {contract_id}")
    contract = await contract_crud.get(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ContractResponse.model_validate(contract)


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: UUID,
    contract_in: ContractUpdate,
    db: AsyncSession = Depends(get_db),
) -> ContractResponse:
    """Update a contract."""
    logger.info(f"Updating contract: {contract_id}")
    contract = await contract_crud.get(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = contract_in.model_dump(exclude_unset=True)
    updated_contract = await contract_crud.update(db, contract, update_data)
    return ContractResponse.model_validate(updated_contract)


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete a contract."""
    logger.info(f"Deleting contract: {contract_id}")
    contract = await contract_crud.get(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    await contract_crud.delete(db, contract_id)
    return {"status": "success", "message": "Contract deleted"}
