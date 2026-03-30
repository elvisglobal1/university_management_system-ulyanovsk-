from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class ApplicationTypeEnum(str, enum.Enum):
    CERTIFICATE = "certificate"
    RETAKE = "retake"
    SCHOLARSHIP = "scholarship"

class ApplicationStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    full_name = Column(String(200))
    role = Column(Enum(RoleEnum), default=RoleEnum.STUDENT)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    grades = relationship("Grade", back_populates="student")
    applications = relationship("Application", back_populates="user")
    taught_schedule = relationship("Schedule", foreign_keys="Schedule.teacher_id")
    announcements = relationship("Announcement", back_populates="teacher")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    students = relationship("User", back_populates="group")
    schedule = relationship("Schedule", back_populates="group")

class Discipline(Base):
    __tablename__ = "disciplines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    credits = Column(Integer, default=3)
    
    schedule = relationship("Schedule", back_populates="discipline")
    grades = relationship("Grade", back_populates="discipline")

class Auditorium(Base):
    __tablename__ = "auditoriums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, default=30)
    
    schedule = relationship("Schedule", back_populates="auditorium")

class Schedule(Base):
    __tablename__ = "schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    auditorium_id = Column(Integer, ForeignKey("auditoriums.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1-7 Monday-Sunday
    start_time = Column(String(5), nullable=False)  # "09:00"
    end_time = Column(String(5), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="schedule")
    teacher = relationship("User", foreign_keys=[teacher_id])
    discipline = relationship("Discipline", back_populates="schedule")
    auditorium = relationship("Auditorium", back_populates="schedule")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    value = Column(Float, nullable=False)
    is_debt = Column(Boolean, default=False)
    semester = Column(String(10), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("User", back_populates="grades")
    discipline = relationship("Discipline", back_populates="grades")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(ApplicationTypeEnum), nullable=False)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.PENDING)
    files = Column(JSON, default=[])  # Store file paths
    total_size = Column(Integer, default=0)  # Total size in bytes
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # NULL = all groups
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    files = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User", back_populates="announcements")
    group = relationship("Group")
