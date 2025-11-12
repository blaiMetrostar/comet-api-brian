from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

import app.cases.services as service
from app.cases.schemas import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseUpdate,
    CaseWithApplicant,
)
from app.db import get_db

router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
    responses={404: {"description": "Endpoint not found"}},
)

# Database dependency injection session
db_session = Annotated[Session, Depends(get_db)]


@router.get("", status_code=status.HTTP_200_OK, response_model=CaseListResponse)
async def get_cases(db: db_session, page_number: int = 0, page_size: int = 100):
    """Retrieve a paginated list of all cases.

    Args:
        db: Database session.
        page_number: Page number for pagination (default: 0).
        page_size: Number of items per page (default: 100).

    Returns:
        CaseListResponse: Paginated list of cases.
    """
    return service.get_items(db, page_number, page_size)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CaseResponse)
async def create_case(case: CaseCreate, db: db_session):
    """Create a new case.

    Args:
        case: Case data to create.
        db: Database session.

    Returns:
        CaseResponse: The created case.
    """
    db_case = service.create_item(db, case)
    return db_case


@router.get(
    "/{case_id}", status_code=status.HTTP_200_OK, response_model=CaseWithApplicant
)
async def get_case(case_id: int, db: db_session):
    """Retrieve a single case by ID with applicant details.

    Args:
        case_id: ID of the case to retrieve.
        db: Database session.

    Returns:
        CaseWithApplicant: The requested case with applicant information.
    """
    return service.get_item(db, case_id)


@router.put("/{case_id}", status_code=status.HTTP_200_OK, response_model=CaseResponse)
async def update_case(case_id: int, case: CaseUpdate, db: db_session):
    """Update an existing case.

    Args:
        case_id: ID of the case to update.
        case: Updated case data.
        db: Database session.

    Returns:
        CaseResponse: The updated case.
    """
    db_case = service.update_item(db, case_id, case)
    return db_case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int, db: db_session):
    """Delete a case.

    Args:
        case_id: ID of the case to delete.
        db: Database session.
    """
    service.delete_item(db, case_id)
