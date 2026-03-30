from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app import models
from app.database import engine, SessionLocal
from app.routers import auth, schedule, grades, applications, announcements
from app.config import settings

# Create tables
models.Base.metadata.create_all(bind=engine)

# Seed initial data
def seed_database():
    db = SessionLocal()
    
    # Check if admin exists
    from app import auth as auth_utils
    from app.models import RoleEnum, Group, Discipline, Auditorium
    
    # Create admin if not exists
    admin = db.query(models.User).filter(models.User.login == "admin").first()
    if not admin:
        admin_user = models.User(
            login="admin",
            password_hash=auth_utils.get_password_hash("admin123"),
            email="admin@university.com",
            full_name="System Administrator",
            role=RoleEnum.ADMIN
        )
        db.add(admin_user)
    
    # Create default groups
    groups = ["CS-2023-1", "CS-2023-2", "IT-2023-1"]
    for g in groups:
        existing = db.query(Group).filter(Group.name == g).first()
        if not existing:
            db.add(Group(name=g))
    
    # Create default disciplines
    disciplines = ["Mathematics", "Programming", "Databases", "Web Development", "Operating Systems"]
    for d in disciplines:
        existing = db.query(Discipline).filter(Discipline.name == d).first()
        if not existing:
            db.add(Discipline(name=d, credits=3))
    
    # Create default auditoriums
    auditoriums = ["101", "102", "201", "202", "301"]
    for a in auditoriums:
        existing = db.query(Auditorium).filter(Auditorium.name == a).first()
        if not existing:
            db.add(Auditorium(name=a, capacity=30))
    
    # Create a sample teacher
    teacher = db.query(models.User).filter(models.User.login == "teacher").first()
    if not teacher:
        teacher_user = models.User(
            login="teacher",
            password_hash=auth_utils.get_password_hash("teacher123"),
            email="teacher@university.com",
            full_name="John Smith",
            role=RoleEnum.TEACHER
        )
        db.add(teacher_user)
    
    db.commit()
    db.close()

# Run seed
seed_database()

app = FastAPI(title="University Management System API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(schedule.router)
app.include_router(grades.router)
app.include_router(applications.router)
app.include_router(announcements.router)

@app.get("/")
def root():
    return {"message": "University Management System API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}