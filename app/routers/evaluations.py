from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import (
    Course,
    Evaluation,
    EvaluationQuestion,
    EvaluationResponse,
    EvaluationAnswer,
)
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationQuestionCreate,
    EvaluationSubmit,
    EvaluationResponseSchema,
    EvaluationQuestionResponse,
    EvaluationSubmissionResponse,
)


router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
)
@router.post(
    "/",
    response_model=EvaluationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation(
    evaluation_data: EvaluationCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == evaluation_data.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    existing_evaluation = (
        db.query(Evaluation)
        .filter(Evaluation.course_id == evaluation_data.course_id)
        .first()
    )

    if existing_evaluation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evaluation already exists for this course",
        )

    evaluation = Evaluation(
        course_id=evaluation_data.course_id,
        title=evaluation_data.title,
        is_active=evaluation_data.is_active,
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation

@router.post(
    "/questions",
    response_model=EvaluationQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation_question(
    question_data: EvaluationQuestionCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    evaluation = (
        db.query(Evaluation)
        .filter(Evaluation.id == question_data.evaluation_id)
        .first()
    )

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    existing_order = (
        db.query(EvaluationQuestion)
        .filter(
            EvaluationQuestion.evaluation_id == question_data.evaluation_id,
            EvaluationQuestion.order == question_data.order,
        )
        .first()
    )

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question order already exists",
        )

    question = EvaluationQuestion(
        evaluation_id=question_data.evaluation_id,
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
    response_model=EvaluationSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_evaluation(
    submission: EvaluationSubmit,
    db: Session = Depends(get_db),
):
    evaluation = (
        db.query(Evaluation)
        .filter(
            Evaluation.id == submission.evaluation_id,
            Evaluation.is_active == True,
        )
        .first()
    )

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active evaluation not found",
        )

    existing_response = (
        db.query(EvaluationResponse)
        .filter(
            EvaluationResponse.evaluation_id == submission.evaluation_id,
            EvaluationResponse.trainee_id == submission.trainee_id,
        )
        .first()
    )

    if existing_response:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evaluation already submitted by this trainee",
        )

    response = EvaluationResponse(
        evaluation_id=submission.evaluation_id,
        trainee_id=submission.trainee_id,
        submitted_at=datetime.now(),
    )

    db.add(response)
    db.flush()

    for answer_data in submission.answers:
        question = (
            db.query(EvaluationQuestion)
            .filter(
                EvaluationQuestion.id == answer_data.question_id,
                EvaluationQuestion.evaluation_id == submission.evaluation_id,
            )
            .first()
        )

        if not question:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question: {answer_data.question_id}",
            )

        answer = EvaluationAnswer(
            response_id=response.id,
            question_id=answer_data.question_id,
            answer_text=answer_data.answer_text,
        )
        db.add(answer)

    db.commit()
    db.refresh(response)

    return response