from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Course, Session as TrainingSession
from app.schemas.session import SessionCreate, SessionResponse


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    session_data: SessionCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == session_data.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    training_session = TrainingSession(
        course_id=session_data.course_id,
        title=session_data.title,
        session_date=session_data.session_date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        meeting_url=session_data.meeting_url,
        attendance_open_at=session_data.attendance_open_at,
        attendance_close_at=session_data.attendance_close_at,
    )

    db.add(training_session)
    db.commit()
    db.refresh(training_session)

    return training_session