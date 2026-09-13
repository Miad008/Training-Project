from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# =========================================================
# Impact Question Type
# =========================================================

class ImpactQuestionType(str, Enum):
    RATING = "rating"
    TEXT = "text"


# =========================================================
# Create Impact Form
# =========================================================

class ImpactFormCreate(BaseModel):
    course_id: int
    title: str
    is_active: bool = True


# =========================================================
# Update Impact Form
# =========================================================

class ImpactFormUpdate(BaseModel):
    title: str | None = None
    is_active: bool | None = None


# =========================================================
# Impact Form Response
# =========================================================

class ImpactFormResponse(BaseModel):
    id: int
    course_id: int
    title: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }


# =========================================================
# Create Impact Question
# =========================================================

class ImpactQuestionCreate(BaseModel):
    impact_form_id: int

    question_text: str

    question_type: ImpactQuestionType

    order: int = Field(gt=0)


# =========================================================
# Update Impact Question
# =========================================================

class ImpactQuestionUpdate(BaseModel):
    question_text: str | None = None

    question_type: ImpactQuestionType | None = None

    order: int | None = Field(default=None, gt=0)


# =========================================================
# Impact Question Response
# =========================================================

class ImpactQuestionResponse(BaseModel):
    id: int
    impact_form_id: int

    question_text: str

    question_type: ImpactQuestionType

    order: int

    model_config = {
        "from_attributes": True
    }


# =========================================================
# Impact Answer
# =========================================================

class ImpactAnswerCreate(BaseModel):
    question_id: int
    answer_text: str


# =========================================================
# Submit Impact Form
# =========================================================

class ImpactSubmit(BaseModel):
    impact_form_id: int
    trainee_id: int
    answers: list[ImpactAnswerCreate]


# =========================================================
# Impact Submission Response
# =========================================================

class ImpactSubmissionResponse(BaseModel):
    id: int

    impact_form_id: int
    trainee_id: int

    submitted_at: datetime

    model_config = {
        "from_attributes": True
    }