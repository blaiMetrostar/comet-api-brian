import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.cases.models import DBCase
from app.cases.schemas import CaseCreate, CaseUpdate
from app.utils import get_next_page, get_page_count, get_prev_page

logger = logging.getLogger(__name__)


def get_items(db: Session, page_number: int, page_size: int):
    """Retrieve a paginated list of cases.

    Args:
        db: Database session.
        page_number: Current page number (0-indexed).
        page_size: Number of items per page.

    Returns:
        dict: Paginated response containing cases and pagination metadata.
    """
    logger.debug("Fetching cases - page: %s, size: %s", page_number, page_size)
    item_count = db.query(DBCase).count()
    items = db.query(DBCase).limit(page_size).offset(page_number * page_size).all()
    logger.info("Retrieved %s cases (total: %s)", len(items), item_count)

    return {
        "items": items,
        "item_count": item_count,
        "page_count": get_page_count(item_count, page_size),
        "prev_page": get_prev_page(page_number),
        "next_page": get_next_page(item_count, page_number, page_size),
    }


def create_item(db: Session, case: CaseCreate):
    """Create a new case in the database.

    Args:
        db: Database session.
        case: Case data to create.

    Returns:
        DBCase: The created case record.
    """
    logger.debug("Creating new case with applicant_id: %s", case.applicant_id)
    db_case = DBCase(**case.model_dump())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    logger.info("Created case with id: %s", db_case.id)

    return db_case


def get_item(db: Session, case_id: int):
    """Retrieve a single case by ID with its associated applicant.

    Args:
        db: Database session.
        case_id: ID of the case to retrieve.

    Returns:
        dict: Case data with applicant information.

    Raises:
        HTTPException: If case is not found (404).
    """
    logger.debug("Fetching case with id: %s", case_id)
    case = (
        db.query(DBCase)
        .options(joinedload(DBCase.applicant))
        .where(DBCase.id == case_id)
        .first()
    )

    if case is None:
        logger.warning("Case not found with id: %s", case_id)
        raise HTTPException(status_code=404, detail="Case not found")

    logger.info("Retrieved case with id: %s", case_id)
    # Handle case where applicant might be None
    applicant_data = None
    if case.applicant:
        applicant_data = {
            "id": case.applicant.id,
            "first_name": case.applicant.first_name,
            "last_name": case.applicant.last_name,
            "middle_name": case.applicant.middle_name,
            "email": case.applicant.email,
            "gender": case.applicant.gender,
            "date_of_birth": case.applicant.date_of_birth,
            "ssn": case.applicant.ssn,
            "home_phone": case.applicant.home_phone,
            "mobile_phone": case.applicant.mobile_phone,
            "address": case.applicant.address,
            "city": case.applicant.city,
            "state": case.applicant.state,
            "zip": case.applicant.zip,
            "country": case.applicant.country,
            "created_at": case.applicant.created_at,
            "updated_at": case.applicant.updated_at,
        }

    return {
        "id": case.id,
        "status": case.status,
        "applicant_id": case.applicant_id,
        "applicant": applicant_data,
        "assigned_to": case.assigned_to,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


def update_item(db: Session, id: int, case: CaseUpdate):
    """Update an existing case.

    Args:
        db: Database session.
        id: ID of the case to update.
        case: Updated case data.

    Returns:
        DBCase: The updated case record.

    Raises:
        HTTPException: If case is not found (404).
    """
    logger.debug("Updating case with id: %s", id)
    db_case = db.query(DBCase).filter(DBCase.id == id).first()
    if db_case is None:
        logger.warning("Case not found for update with id: %s", id)
        raise HTTPException(status_code=404, detail="Case not found")

    # Update only the fields that are explicitly set in the request
    update_data = case.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)

    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    logger.info("Updated case with id: %s", id)

    return db_case


def delete_item(db: Session, id: int):
    """Delete a case from the database.

    Args:
        db: Database session.
        id: ID of the case to delete.

    Returns:
        None

    Raises:
        HTTPException: If case is not found (404).
    """
    logger.debug("Deleting case with id: %s", id)
    db_case = db.query(DBCase).filter(DBCase.id == id).first()
    if db_case is None:
        logger.warning("Case not found for deletion with id: %s", id)
        raise HTTPException(status_code=404, detail="Case not found")

    db.query(DBCase).filter(DBCase.id == id).delete()
    db.commit()
    logger.info("Deleted case with id: %s", id)

    return None
