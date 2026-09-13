from enum import Enum

from pydantic import BaseModel, Field


# =========================================================
# Course Content Type
# =========================================================

class CourseContentType(str, Enum):
    VIDEO = "video"
    MATERIAL = "material"
    FILE = "file"
    LINK = "link"


# =========================================================
# Create Course Content
# =========================================================

class CourseContentCreate(BaseModel):
    course_id: int

    title: str
    description: str | None = None

    type: CourseContentType

    content_url: str | None = None

    order: int = Field(gt=0)

    is_required: bool = True


# =========================================================
# Update Course Content
# =========================================================

class CourseContentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    type: CourseContentType | None = None

    content_url: str | None = None

    order: int | None = Field(default=None, gt=0)

    is_required: bool | None = None


# =========================================================
# Course Content Response
# =========================================================

class CourseContentResponse(BaseModel):
    id: int
    course_id: int

    title: str
    description: str | None

    type: CourseContentType

    content_url: str | None

    order: int

    is_required: bool

    model_config = {
        "from_attributes": True
    }