from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserCreate(BaseModel):
    login: str = Field(..., min_length=5, max_length=100)
    email: EmailStr
    full_name: str
    group_id: Optional[int] = None
    
    @validator('login')
    def validate_login(cls, v):
        if not v:
            raise ValueError('Login cannot be empty')
        return v

class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    full_name: str
    role: Role
    group_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    login: str
    password: str

class PasswordResetRequest(BaseModel):
    login: str
    email: str

class GradeCreate(BaseModel):
    student_id: int
    discipline_id: int
    value: float = Field(..., ge=0, le=100)
    semester: str

class GradeResponse(BaseModel):
    id: int
    discipline_name: str
    value: float
    is_debt: bool
    semester: str
    date: datetime

class ScheduleResponse(BaseModel):
    id: int
    discipline_name: str
    teacher_name: str
    auditorium_name: str
    day_of_week: int
    start_time: str
    end_time: str
    group_name: str

class ApplicationCreate(BaseModel):
    type: str
    description: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    type: str
    status: str
    files: List[str]
    description: Optional[str]
    created_at: datetime

class AnnouncementCreate(BaseModel):
    group_id: Optional[int]
    title: str
    content: str

class AnnouncementResponse(BaseModel):
    id: int
    teacher_name: str
    group_name: Optional[str]
    title: str
    content: str
    files: List[str]
    created_at: datetime