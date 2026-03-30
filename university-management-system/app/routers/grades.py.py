from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api/grades", tags=["grades"])

@router.get("/my-grades", response_model=List[schemas.GradeResponse])
def get_my_grades(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if current_user.role != models.RoleEnum.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can view grades")
    
    grades = db.query(models.Grade).filter(
        models.Grade.student_id == current_user.id
    ).all()
    
    result = []
    for g in grades:
        result.append(schemas.GradeResponse(
            id=g.id,
            discipline_name=g.discipline.name,
            value=g.value,
            is_debt=g.is_debt,
            semester=g.semester,
            date=g.date
        ))
    
    return result

@router.get("/debts", response_model=List[schemas.GradeResponse])
def get_my_debts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if current_user.role != models.RoleEnum.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can view debts")
    
    debts = db.query(models.Grade).filter(
        models.Grade.student_id == current_user.id,
        models.Grade.is_debt == True
    ).all()
    
    result = []
    for d in debts:
        result.append(schemas.GradeResponse(
            id=d.id,
            discipline_name=d.discipline.name,
            value=d.value,
            is_debt=d.is_debt,
            semester=d.semester,
            date=d.date
        ))
    
    return result

@router.get("/teacher/gradesheet/{discipline_id}")
def get_grade_sheet(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.RoleEnum.TEACHER))
):
    # Check if teacher teaches this discipline
    teaches = db.query(models.Schedule).filter(
        models.Schedule.teacher_id == current_user.id,
        models.Schedule.discipline_id == discipline_id
    ).first()
    
    if not teaches:
        raise HTTPException(status_code=403, detail="You don't teach this discipline")
    
    grades = db.query(models.Grade).filter(
        models.Grade.discipline_id == discipline_id
    ).all()
    
    return grades

@router.post("/teacher/grade")
def add_grade(
    grade_data: schemas.GradeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.RoleEnum.TEACHER))
):
    # Verify teacher teaches this discipline
    teaches = db.query(models.Schedule).filter(
        models.Schedule.teacher_id == current_user.id,
        models.Schedule.discipline_id == grade_data.discipline_id
    ).first()
    
    if not teaches:
        raise HTTPException(status_code=403, detail="You don't teach this discipline")
    
    # Check if student is in teacher's group
    student = db.query(models.User).filter(models.User.id == grade_data.student_id).first()
    if not student or student.group_id != teaches.group_id:
        raise HTTPException(status_code=400, detail="Student not in your group")
    
    grade = models.Grade(
        student_id=grade_data.student_id,
        discipline_id=grade_data.discipline_id,
        value=grade_data.value,
        is_debt=grade_data.value < 60,
        semester=grade_data.semester
    )
    
    db.add(grade)
    db.commit()
    db.refresh(grade)
    
    return grade