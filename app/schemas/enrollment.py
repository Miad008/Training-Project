from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# =========================================================
# Enrollment Status
# =========================================================

class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# =========================================================
# Create Enrollment
# =========================================================

class EnrollmentCreate(BaseModel):
    trainee_id: int
    course_id: int


# =========================================================
# Update Enrollment
# =========================================================

class EnrollmentUpdate(BaseModel):
    status: EnrollmentStatus
    rejection_reason: str | None = None


# =========================================================
# Enrollment Response
# =========================================================

class EnrollmentResponse(BaseModel):
    id: int

    trainee_id: int
    course_id: int

    registered_at: datetime

    status: EnrollmentStatus

    rejection_reason: str | None

    model_config = {
        "from_attributes": True
    }
    