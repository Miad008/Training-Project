from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CertificateStatus(str, Enum):
    ISSUED = "issued"
    REVOKED = "revoked"


class CertificateCreate(BaseModel):
    trainee_id: int
    course_id: int


class CertificateUpdate(BaseModel):
    status: CertificateStatus


class CertificateResponse(BaseModel):
    id: int
    trainee_id: int
    course_id: int
    certificate_number: str
    issued_at: datetime
    status: CertificateStatus
    file_path: str | None

    model_config = {
        "from_attributes": True
    }