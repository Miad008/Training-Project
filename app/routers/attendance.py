from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import (
    Attendance,
    Course,
    Enrollment,
    Session as TrainingSession,
    User,
)
from app.schemas.attendance import AttendanceCreate, AttendanceResponse


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    attendance_data: AttendanceCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    # 1. التأكد أن المتدرب موجود وأن دوره Trainee
    trainee = (
        db.query(User)
        .filter(
            User.id == attendance_data.trainee_id,
            User.role == "trainee",
        )
        .first()
    )

    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee not found",
        )

    # 2. التأكد أن الدورة موجودة
    course = (
        db.query(Course)
        .filter(Course.id == attendance_data.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # 3. التأكد أن الجلسة موجودة وتابعة لنفس الدورة
    training_session = (
        db.query(TrainingSession)
        .filter(
            TrainingSession.id == attendance_data.session_id,
            TrainingSession.course_id == attendance_data.course_id,
        )
        .first()
    )

    if not training_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found for this course",
        )

    # 4. التأكد أن المتدرب مقبول في الدورة
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.trainee_id == attendance_data.trainee_id,
            Enrollment.course_id == attendance_data.course_id,
            Enrollment.status == "approved",
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trainee is not approved for this course",
        )

    # 5. منع تسجيل الحضور مرتين لنفس المتدرب في نفس الجلسة
    existing_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.trainee_id == attendance_data.trainee_id,
            Attendance.session_id == attendance_data.session_id,
        )
        .first()
    )

    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance already recorded for this session",
        )

    # 6. إنشاء سجل الحضور
    attendance = Attendance(
        trainee_id=attendance_data.trainee_id,
        course_id=attendance_data.course_id,
        session_id=attendance_data.session_id,
        attendance_status=attendance_data.attendance_status.value,
        recorded_at=datetime.now(),
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance