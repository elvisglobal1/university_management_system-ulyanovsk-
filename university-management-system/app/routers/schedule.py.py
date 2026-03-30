from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.get("/", response_model=List[schemas.ScheduleResponse])
def get_schedule(
    group_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    auditorium_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Schedule)
    
    if group_id:
        query = query.filter(models.Schedule.group_id == group_id)
    if teacher_id:
        query = query.filter(models.Schedule.teacher_id == teacher_id)
    if auditorium_id:
        query = query.filter(models.Schedule.auditorium_id == auditorium_id)
    
    schedule = query.all()
    
    result = []
    for s in schedule:
        result.append(schemas.ScheduleResponse(
            id=s.id,
            discipline_name=s.discipline.name,
            teacher_name=s.teacher.full_name,
            auditorium_name=s.auditorium.name,
            day_of_week=s.day_of_week,
            start_time=s.start_time,
            end_time=s.end_time,
            group_name=s.group.name
        ))
    
    return result