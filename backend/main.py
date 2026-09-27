from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import API_PREFIX, FRONTEND_ORIGINS
from backend.api import students, assessments, progress, interventions, teachers, resources, facilitator, ai_assistant, curriculum, teacher_authoring, subjects
from backend.database.database import initialize_database

app = FastAPI(
    title="HackMysore 1.0 - Personalized Learning API",
    version="1.0.0",
    description="Backend and adaptive-learning engine for the Personalized Learning MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix=API_PREFIX)
app.include_router(assessments.router, prefix=API_PREFIX)
app.include_router(progress.router, prefix=API_PREFIX)
app.include_router(interventions.router, prefix=API_PREFIX)
app.include_router(teachers.router, prefix=API_PREFIX)
app.include_router(resources.router, prefix=API_PREFIX)
app.include_router(facilitator.router, prefix=API_PREFIX)
app.include_router(ai_assistant.router, prefix=API_PREFIX)
app.include_router(curriculum.router, prefix=API_PREFIX)
app.include_router(teacher_authoring.router, prefix=API_PREFIX)
app.include_router(subjects.router, prefix=API_PREFIX)


@app.on_event("startup")
def startup():
    # Creates tables if the shared DB has not been initialized yet.
    # It never inserts demo data and never resets an existing database.
    initialize_database()


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "message": "One or more request fields are invalid."},
    )


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected server error occurred."},
    )

# Serve the vanilla HTML/CSS/JS frontend from the same FastAPI process.
# API routes above remain available under /api and /docs.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
