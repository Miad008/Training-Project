from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import analytics

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(analytics.router)


@app.get("/")
def home():
    return {"message": "Training Management System"}
