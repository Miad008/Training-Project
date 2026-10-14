from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routers import analytics, attendance, auth, courses, enrollments, evaluations, impacts, sessions

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(sessions.router)
app.include_router(attendance.router)
app.include_router(evaluations.router)
app.include_router(impacts.router)

@app.get("/")
def home():
    return {"message": "Training Management System"}