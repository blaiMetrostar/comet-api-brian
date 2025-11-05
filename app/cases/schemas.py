from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.applicants.schemas import ApplicantResponse

# Constants
CASE_STATUS = Literal["Not Started", "In Progress", "Approved", "Denied"]


# Pydantic Models
class CaseBase(BaseModel):
    """Base Pydantic model for case data.

    Contains common fields shared across create, update, and response models.
    """

    status: CASE_STATUS
    assigned_to: str | None = Field(None, min_length=1, max_length=255)


class CaseCreate(CaseBase):
    """Pydantic model for creating a new case.

    Requires an applicant_id to associate the case with an applicant.
    """

    applicant_id: int


class CaseUpdate(BaseModel):
    """Pydantic model for updating an existing case.

    All fields are optional to support partial updates.
    """

    status: CASE_STATUS | None = None
    assigned_to: str | None = None


class CaseResponse(CaseBase):
    """Pydantic model for case API responses.

    Includes database-generated fields like id, applicant_id,
    created_at, and updated_at.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    applicant_id: int
    created_at: datetime
    updated_at: datetime


class CaseWithApplicant(CaseResponse):
    """Pydantic model for case responses with applicant details.

    Extends CaseResponse to include the full applicant information.
    """

    applicant: ApplicantResponse | None = None


class CaseListResponse(BaseModel):
    """Pydantic model for paginated list of cases.

    Contains pagination metadata along with the list of cases.
    """

    items: list[CaseWithApplicant]
    item_count: int
    page_count: int
    prev_page: int | None = None
    next_page: int | None = None
