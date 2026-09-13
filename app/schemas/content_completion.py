from datetime import datetime

from pydantic import BaseModel


# =========================================================
# Create Content Completion
# =========================================================

class ContentCompletionCreate(BaseModel):
    trainee_id: int
    course_id: int
    content_id: int


# =========================================================
# Content Completion Response
# =========================================================

class ContentCompletionResponse(BaseModel):
    id: int

    trainee_id: int
    course_id: int
    content_id: int

    completed_at: datetime

    model_config = {
        "from_attributes": True
    }