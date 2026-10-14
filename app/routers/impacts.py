from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import (
    Course,
    ImpactForm,
    ImpactQuestion,
    ImpactResponse,
    ImpactAnswer,
)
from app.schemas.impact import (
    ImpactFormCreate,
    ImpactQuestionCreate,
    ImpactSubmit,
    ImpactFormResponse,
    ImpactQuestionResponse,
    ImpactSubmissionResponse,
)


router = APIRouter(
    prefix="/impacts",
    tags=["Impacts"],
)


@router.post(
    "/",
    response_model=ImpactFormResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_impact_form(
    form_data: ImpactFormCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == form_data.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    existing_form = (
        db.query(ImpactForm)
        .filter(ImpactForm.course_id == form_data.course_id)
        .first()
    )

    if existing_form:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impact form already exists for this course",
        )

    impact_form = ImpactForm(
        course_id=form_data.course_id,
        title=form_data.title,
        is_active=form_data.is_active,
    )

    db.add(impact_form)
    db.commit()
    db.refresh(impact_form)

    return impact_form


@router.post(
    "/questions",
    response_model=ImpactQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_impact_question(
    question_data: ImpactQuestionCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    impact_form = (
        db.query(ImpactForm)
        .filter(ImpactForm.id == question_data.impact_form_id)
        .first()
    )

    if not impact_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impact form not found",
        )

    existing_order = (
        db.query(ImpactQuestion)
        .filter(
            ImpactQuestion.impact_form_id == question_data.impact_form_id,
            ImpactQuestion.order == question_data.order,
        )
        .first()
    )

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question order already exists",
        )

    question = ImpactQuestion(
        impact_form_id=question_data.impact_form_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type.value,
        order=question_data.order,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


@router.post(
    "/submit",
    response_model=ImpactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_impact(
    submission: ImpactSubmit,
    db: Session = Depends(get_db),
):
    impact_form = (
        db.query(ImpactForm)
        .filter(
            ImpactForm.id == submission.impact_form_id,
            ImpactForm.is_active == True,
        )
        .first()
    )

    if not impact_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active impact form not found",
        )

    existing_response = (
        db.query(ImpactResponse)
        .filter(
            ImpactResponse.impact_form_id == submission.impact_form_id,
            ImpactResponse.trainee_id == submission.trainee_id,
        )
        .first()
    )

    if existing_response:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impact form already submitted by this trainee",
        )

    questions = (
        db.query(ImpactQuestion)
        .filter(ImpactQuestion.impact_form_id == submission.impact_form_id)
        .all()
    )

    expected_ids = {question.id for question in questions}
    submitted_ids = [answer.question_id for answer in submission.answers]

    if not expected_ids or set(submitted_ids) != expected_ids or len(submitted_ids) != len(expected_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All impact questions must be answered exactly once",
        )

    for question in questions:
        answer = next(
            item for item in submission.answers
            if item.question_id == question.id
        )

        if question.question_type == "rating":
            if answer.answer_text not in {"1", "2", "3", "4", "5"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5",
                )

    response = ImpactResponse(
        impact_form_id=submission.impact_form_id,
        trainee_id=submission.trainee_id,
        submitted_at=datetime.now(),
    )

    db.add(response)
    db.flush()

    for answer_data in submission.answers:
        db.add(
            ImpactAnswer(
                response_id=response.id,
                question_id=answer_data.question_id,
                answer_text=answer_data.answer_text,
            )
        )

    db.commit()
    db.refresh(response)

    return response