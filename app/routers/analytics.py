from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Enrollment,
    Attendance,
    Session,
    Course,
    CourseContent,
    ContentCompletion,
    Evaluation,
    EvaluationQuestion,
    EvaluationResponse,
    EvaluationAnswer,
    ImpactForm,
    ImpactQuestion,
    ImpactResponse,
    ImpactAnswer

)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# =========================================================
# 1. Registration Count
# =========================================================

@router.get("/courses/{course_id}/registrations")
def get_course_registrations(
    course_id: int,
    db: Session = Depends(get_db)
):
    registered_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .count()
    )

    return {
        "course_id": course_id,
        "registered_trainees": registered_count
    }


# =========================================================
# 2. Attendance & Absence Rate
# =========================================================

@router.get("/courses/{course_id}/attendance")
def get_course_attendance(
    course_id: int,
    db: Session = Depends(get_db)
):
    total_records = (
        db.query(Attendance)
        .filter(Attendance.course_id == course_id)
        .count()
    )

    present_count = (
        db.query(Attendance)
        .filter(
            Attendance.course_id == course_id,
            Attendance.attendance_status == "present"
        )
        .count()
    )

    absent_count = (
        db.query(Attendance)
        .filter(
            Attendance.course_id == course_id,
            Attendance.attendance_status == "absent"
        )
        .count()
    )

    if total_records == 0:
        attendance_rate = 0
        absence_rate = 0
    else:
        attendance_rate = round(
            (present_count / total_records) * 100,
            2
        )

        absence_rate = round(
            (absent_count / total_records) * 100,
            2
        )

    return {
        "course_id": course_id,
        "total_attendance_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_rate": attendance_rate,
        "absence_rate": absence_rate
    }


# =========================================================
# 3. Session Attendance
# =========================================================

@router.get("/courses/{course_id}/sessions-attendance")
def get_sessions_attendance(
    course_id: int,
    db: Session = Depends(get_db)
):
    sessions = (
        db.query(Session)
        .filter(Session.course_id == course_id)
        .all()
    )

    result = []

    for session in sessions:
        present_count = (
            db.query(Attendance)
            .filter(
                Attendance.course_id == course_id,
                Attendance.session_id == session.id,
                Attendance.attendance_status == "present"
            )
            .count()
        )

        result.append({
            "session_id": session.id,
            "session_title": session.title,
            "present_count": present_count
        })

    return result


# =========================================================
# 4. Seat Occupancy / Participant Capacity
# =========================================================

@router.get("/courses/{course_id}/seat-occupancy")
def get_seat_occupancy(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        return {
            "message": "Course not found"
        }

    registered_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .count()
    )

    minimum_participants = course.minimum_participants
    maximum_participants = course.maximum_participants

    # Check whether the minimum number of participants
    # has been reached.
    if minimum_participants is None:
        minimum_reached = True
    else:
        minimum_reached = (
            registered_count >= minimum_participants
        )

    # If maximum_participants is NULL,
    # the course has unlimited capacity.
    if maximum_participants is None:
        capacity_type = "unlimited"
        available_seats = None
        occupancy_rate = None
        is_full = False

    else:
        capacity_type = "limited"

        available_seats = max(
            maximum_participants - registered_count,
            0
        )

        occupancy_rate = round(
            (registered_count / maximum_participants) * 100,
            2
        )

        is_full = (
            registered_count >= maximum_participants
        )

    return {
        "course_id": course_id,
        "minimum_participants": minimum_participants,
        "maximum_participants": maximum_participants,
        "registered_trainees": registered_count,
        "minimum_reached": minimum_reached,
        "capacity_type": capacity_type,
        "available_seats": available_seats,
        "occupancy_rate": occupancy_rate,
        "is_full": is_full
    }


# =========================================================
# 5. Content Completion
# =========================================================

@router.get("/courses/{course_id}/content-completion")
def get_content_completion(
    course_id: int,
    db: Session = Depends(get_db)
):
    # Count only required course content.
    required_contents = (
        db.query(CourseContent)
        .filter(
            CourseContent.course_id == course_id,
            CourseContent.is_required == True
        )
        .all()
    )

    total_required_contents = len(required_contents)

    required_content_ids = [
        content.id for content in required_contents
    ]

    # Get approved trainees only.
    approved_enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .all()
    )

    trainees = []

    for enrollment in approved_enrollments:
        if total_required_contents == 0:
            completed_required_contents = 0
            completion_rate = 0

        else:
            completed_required_contents = (
                db.query(ContentCompletion)
                .filter(
                    ContentCompletion.course_id == course_id,
                    ContentCompletion.trainee_id == enrollment.trainee_id,
                    ContentCompletion.content_id.in_(
                        required_content_ids
                    )
                )
                .count()
            )

            completion_rate = round(
                (
                    completed_required_contents
                    / total_required_contents
                ) * 100,
                2
            )

        trainees.append({
            "trainee_id": enrollment.trainee_id,
            "completed_required_contents": completed_required_contents,
            "total_required_contents": total_required_contents,
            "completion_rate": completion_rate,
            "is_completed": completion_rate == 100
        })

    return {
        "course_id": course_id,
        "total_required_contents": total_required_contents,
        "trainees": trainees
    }


# =========================================================
# 6. Evaluation Analytics
# =========================================================

@router.get("/courses/{course_id}/evaluation")
def get_evaluation_analytics(
    course_id: int,
    db: Session = Depends(get_db)
):
    # Get the active evaluation for the course.
    evaluation = (
        db.query(Evaluation)
        .filter(
            Evaluation.course_id == course_id,
            Evaluation.is_active == True
        )
        .first()
    )

    if not evaluation:
        return {
            "course_id": course_id,
            "message": "No active evaluation found"
        }

    # Count approved trainees.
    approved_trainees = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .count()
    )

    # Count submitted evaluation responses.
    submitted_responses = (
        db.query(EvaluationResponse)
        .filter(
            EvaluationResponse.evaluation_id == evaluation.id
        )
        .count()
    )

    # Calculate evaluation response rate.
    if approved_trainees == 0:
        response_rate = 0
    else:
        response_rate = round(
            (submitted_responses / approved_trainees) * 100,
            2
        )

    # Get rating questions only.
    rating_questions = (
        db.query(EvaluationQuestion)
        .filter(
            EvaluationQuestion.evaluation_id == evaluation.id,
            EvaluationQuestion.question_type == "rating"
        )
        .order_by(EvaluationQuestion.order)
        .all()
    )

    question_averages = []
    all_ratings = []

    for question in rating_questions:
        answers = (
            db.query(EvaluationAnswer)
            .join(
                EvaluationResponse,
                EvaluationAnswer.response_id == EvaluationResponse.id
            )
            .filter(
                EvaluationResponse.evaluation_id == evaluation.id,
                EvaluationAnswer.question_id == question.id
            )
            .all()
        )

        ratings = []

        for answer in answers:
            try:
                rating = float(answer.answer_text)

                if 1 <= rating <= 5:
                    ratings.append(rating)
                    all_ratings.append(rating)

            except (ValueError, TypeError):
                continue

        if ratings:
            average_rating = round(
                sum(ratings) / len(ratings),
                2
            )
        else:
            average_rating = 0

        question_averages.append({
            "question_id": question.id,
            "question": question.question_text,
            "responses": len(ratings),
            "average_rating": average_rating
        })

    # Calculate overall evaluation average.
    if all_ratings:
        overall_average = round(
            sum(all_ratings) / len(all_ratings),
            2
        )
    else:
        overall_average = 0

    return {
        "course_id": course_id,
        "evaluation_id": evaluation.id,
        "approved_trainees": approved_trainees,
        "submitted_responses": submitted_responses,
        "response_rate": response_rate,
        "overall_average": overall_average,
        "question_averages": question_averages
    }

# =========================================================
# 7. Impact Analytics
# =========================================================

@router.get("/courses/{course_id}/impact")
def get_impact_analytics(
    course_id: int,
    db: Session = Depends(get_db)
):
    # Get the active impact form for the course.
    impact_form = (
        db.query(ImpactForm)
        .filter(
            ImpactForm.course_id == course_id,
            ImpactForm.is_active == True
        )
        .first()
    )

    if not impact_form:
        return {
            "course_id": course_id,
            "message": "No active impact form found"
        }

    # Count approved trainees.
    approved_trainees = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .count()
    )

    # Count submitted impact responses.
    submitted_responses = (
        db.query(ImpactResponse)
        .filter(
            ImpactResponse.impact_form_id == impact_form.id
        )
        .count()
    )

    # Calculate impact response rate.
    if approved_trainees == 0:
        response_rate = 0
    else:
        response_rate = round(
            (submitted_responses / approved_trainees) * 100,
            2
        )

    # Get rating questions only.
    rating_questions = (
        db.query(ImpactQuestion)
        .filter(
            ImpactQuestion.impact_form_id == impact_form.id,
            ImpactQuestion.question_type == "rating"
        )
        .order_by(ImpactQuestion.order)
        .all()
    )

    question_averages = []
    all_ratings = []

    for question in rating_questions:
        answers = (
            db.query(ImpactAnswer)
            .join(
                ImpactResponse,
                ImpactAnswer.response_id == ImpactResponse.id
            )
            .filter(
                ImpactResponse.impact_form_id == impact_form.id,
                ImpactAnswer.question_id == question.id
            )
            .all()
        )

        ratings = []

        for answer in answers:
            try:
                rating = float(answer.answer_text)

                if 1 <= rating <= 5:
                    ratings.append(rating)
                    all_ratings.append(rating)

            except (ValueError, TypeError):
                continue

        if ratings:
            average_rating = round(
                sum(ratings) / len(ratings),
                2
            )
        else:
            average_rating = 0

        question_averages.append({
            "question_id": question.id,
            "question": question.question_text,
            "responses": len(ratings),
            "average_rating": average_rating
        })

    # Calculate overall impact score.
    if all_ratings:
        overall_impact_score = round(
            sum(all_ratings) / len(all_ratings),
            2
        )
    else:
        overall_impact_score = 0

    return {
        "course_id": course_id,
        "impact_form_id": impact_form.id,
        "approved_trainees": approved_trainees,
        "submitted_responses": submitted_responses,
        "response_rate": response_rate,
        "overall_impact_score": overall_impact_score,
        "question_averages": question_averages
    }

# =========================================================
# 8. Course Dashboard Summary
# =========================================================

@router.get("/courses/{course_id}/dashboard")
def get_course_dashboard(
    course_id: int,
    db: Session = Depends(get_db)
):
    # Check that the course exists.
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        return {
            "message": "Course not found"
        }

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    registered_trainees = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .count()
    )

    # -----------------------------------------------------
    # Capacity
    # -----------------------------------------------------

    maximum_participants = course.maximum_participants

    if maximum_participants is None:
        capacity_type = "unlimited"
        occupancy_rate = None
    else:
        capacity_type = "limited"
        occupancy_rate = round(
            (registered_trainees / maximum_participants) * 100,
            2
        )

    # -----------------------------------------------------
    # Attendance
    # -----------------------------------------------------

    total_attendance_records = (
        db.query(Attendance)
        .filter(Attendance.course_id == course_id)
        .count()
    )

    present_count = (
        db.query(Attendance)
        .filter(
            Attendance.course_id == course_id,
            Attendance.attendance_status == "present"
        )
        .count()
    )

    absent_count = (
        db.query(Attendance)
        .filter(
            Attendance.course_id == course_id,
            Attendance.attendance_status == "absent"
        )
        .count()
    )

    if total_attendance_records == 0:
        attendance_rate = 0
        absence_rate = 0
    else:
        attendance_rate = round(
            (present_count / total_attendance_records) * 100,
            2
        )

        absence_rate = round(
            (absent_count / total_attendance_records) * 100,
            2
        )

    # -----------------------------------------------------
    # Content Completion
    # -----------------------------------------------------

    required_contents = (
        db.query(CourseContent)
        .filter(
            CourseContent.course_id == course_id,
            CourseContent.is_required == True
        )
        .all()
    )

    required_content_ids = [
        content.id for content in required_contents
    ]

    total_required_contents = len(required_contents)
    completed_trainees = 0

    approved_enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "approved"
        )
        .all()
    )

    if total_required_contents > 0:
        for enrollment in approved_enrollments:
            completed_count = (
                db.query(ContentCompletion)
                .filter(
                    ContentCompletion.course_id == course_id,
                    ContentCompletion.trainee_id == enrollment.trainee_id,
                    ContentCompletion.content_id.in_(
                        required_content_ids
                    )
                )
                .count()
            )

            if completed_count == total_required_contents:
                completed_trainees += 1

    if registered_trainees == 0:
        content_completion_rate = 0
    else:
        content_completion_rate = round(
            (completed_trainees / registered_trainees) * 100,
            2
        )

    # -----------------------------------------------------
    # Evaluation
    # -----------------------------------------------------

    evaluation = (
        db.query(Evaluation)
        .filter(
            Evaluation.course_id == course_id,
            Evaluation.is_active == True
        )
        .first()
    )

    evaluation_response_rate = 0
    evaluation_average = 0

    if evaluation:
        evaluation_responses = (
            db.query(EvaluationResponse)
            .filter(
                EvaluationResponse.evaluation_id == evaluation.id
            )
            .count()
        )

        if registered_trainees > 0:
            evaluation_response_rate = round(
                (evaluation_responses / registered_trainees) * 100,
                2
            )

        rating_questions = (
            db.query(EvaluationQuestion)
            .filter(
                EvaluationQuestion.evaluation_id == evaluation.id,
                EvaluationQuestion.question_type == "rating"
            )
            .all()
        )

        rating_question_ids = [
            question.id for question in rating_questions
        ]

        if rating_question_ids:
            answers = (
                db.query(EvaluationAnswer)
                .join(
                    EvaluationResponse,
                    EvaluationAnswer.response_id == EvaluationResponse.id
                )
                .filter(
                    EvaluationResponse.evaluation_id == evaluation.id,
                    EvaluationAnswer.question_id.in_(
                        rating_question_ids
                    )
                )
                .all()
            )

            ratings = []

            for answer in answers:
                try:
                    rating = float(answer.answer_text)

                    if 1 <= rating <= 5:
                        ratings.append(rating)

                except (ValueError, TypeError):
                    continue

            if ratings:
                evaluation_average = round(
                    sum(ratings) / len(ratings),
                    2
                )

    # -----------------------------------------------------
    # Impact
    # -----------------------------------------------------

    impact_form = (
        db.query(ImpactForm)
        .filter(
            ImpactForm.course_id == course_id,
            ImpactForm.is_active == True
        )
        .first()
    )

    impact_response_rate = 0
    impact_score = 0

    if impact_form:
        impact_responses = (
            db.query(ImpactResponse)
            .filter(
                ImpactResponse.impact_form_id == impact_form.id
            )
            .count()
        )

        if registered_trainees > 0:
            impact_response_rate = round(
                (impact_responses / registered_trainees) * 100,
                2
            )

        impact_questions = (
            db.query(ImpactQuestion)
            .filter(
                ImpactQuestion.impact_form_id == impact_form.id,
                ImpactQuestion.question_type == "rating"
            )
            .all()
        )

        impact_question_ids = [
            question.id for question in impact_questions
        ]

        if impact_question_ids:
            answers = (
                db.query(ImpactAnswer)
                .join(
                    ImpactResponse,
                    ImpactAnswer.response_id == ImpactResponse.id
                )
                .filter(
                    ImpactResponse.impact_form_id == impact_form.id,
                    ImpactAnswer.question_id.in_(
                        impact_question_ids
                    )
                )
                .all()
            )

            ratings = []

            for answer in answers:
                try:
                    rating = float(answer.answer_text)

                    if 1 <= rating <= 5:
                        ratings.append(rating)

                except (ValueError, TypeError):
                    continue

            if ratings:
                impact_score = round(
                    sum(ratings) / len(ratings),
                    2
                )

    # -----------------------------------------------------
    # Dashboard Summary
    # -----------------------------------------------------

    return {
        "course_id": course_id,
        "course_name": course.name,

        "registration": {
            "registered_trainees": registered_trainees
        },

        "capacity": {
            "capacity_type": capacity_type,
            "maximum_participants": maximum_participants,
            "occupancy_rate": occupancy_rate
        },

        "attendance": {
            "attendance_rate": attendance_rate,
            "absence_rate": absence_rate
        },

        "content": {
            "completed_trainees": completed_trainees,
            "completion_rate": content_completion_rate
        },

        "evaluation": {
            "response_rate": evaluation_response_rate,
            "average": evaluation_average
        },

        "impact": {
            "response_rate": impact_response_rate,
            "score": impact_score
        }
    }