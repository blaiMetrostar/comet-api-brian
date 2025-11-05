from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.applicants.models import DBApplicant
from app.applicants.schemas import ApplicantCreate, ApplicantUpdate
from app.utils import get_next_page, get_page_count, get_prev_page


def get_items(db: Session, page_number: int, page_size: int):
    """Retrieve a paginated list of applicants.

    Args:
        db: Database session.
        page_number: Current page number (0-indexed).
        page_size: Number of items per page.

    Returns:
        dict: Paginated response containing applicants and pagination metadata.
    """
    item_count = db.query(DBApplicant).count()
    items = db.query(DBApplicant).limit(page_size).offset(page_number * page_size).all()

    return {
        "items": items,
        "item_count": item_count,
        "page_count": get_page_count(item_count, page_size),
        "prev_page": get_prev_page(page_number),
        "next_page": get_next_page(item_count, page_number, page_size),
    }


def create_item(db: Session, applicant: ApplicantCreate):
    """Create a new applicant in the database.

    Args:
        db: Database session.
        applicant: Applicant data to create.

    Returns:
        DBApplicant: The created applicant record.
    """
    db_applicant = DBApplicant(**applicant.model_dump())
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)

    return db_applicant


def get_item(db: Session, applicant_id: int):
    """Retrieve a single applicant by ID.

    Args:
        db: Database session.
        applicant_id: ID of the applicant to retrieve.

    Returns:
        DBApplicant | None: The applicant record if found, None otherwise.
    """
    return db.query(DBApplicant).where(DBApplicant.id == applicant_id).first()


def update_item(db: Session, id: int, applicant: ApplicantUpdate):
    """Update an existing applicant.

    Args:
        db: Database session.
        id: ID of the applicant to update.
        applicant: Updated applicant data.

    Returns:
        DBApplicant: The updated applicant record.

    Raises:
        HTTPException: If applicant is not found (404).
    """
    db_applicant = db.query(DBApplicant).filter(DBApplicant.id == id).first()
    if db_applicant is None:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Only update fields that are provided (not None)
    update_data = applicant.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_applicant, field, value)

    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)

    return db_applicant


def delete_item(db: Session, id: int):
    """Delete an applicant from the database.

    Args:
        db: Database session.
        id: ID of the applicant to delete.

    Returns:
        None

    Raises:
        HTTPException: If applicant is not found (404).
    """
    db_applicant = db.query(DBApplicant).filter(DBApplicant.id == id).first()
    if db_applicant is None:
        raise HTTPException(status_code=404, detail="Applicant not found")

    db.query(DBApplicant).filter(DBApplicant.id == id).delete()
    db.commit()

    return None
