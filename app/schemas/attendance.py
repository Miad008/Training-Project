from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# =========================================================
# Attendance Status
# =========================================================

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"


# =========================================================
# Create Attendance
# =========================================================

class AttendanceCreate(BaseModel):
    trainee_id: int
    course_id: int
    session_id: int
    attendance_status: AttendanceStatus


# =========================================================
# Update Attendance
# =========================================================

class AttendanceUpdate(BaseModel):
    attendance_status: AttendanceStatus


# =========================================================
# Attendance Response
# =========================================================

class AttendanceResponse(BaseModel):
    id: int

    trainee_id: int
    course_id: int
    session_id: int

    attendance_status: AttendanceStatus

    recorded_at: datetime

    model_config = {
        "from_attributes": True
    }