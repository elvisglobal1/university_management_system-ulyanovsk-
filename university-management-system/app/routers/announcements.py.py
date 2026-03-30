from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, auth
from app.database import get_db
from app.services.file_service import save_file

router = APIRouter(prefix="/api/announcements", tags=["announcements"])

@router.post("/create")
async def create_announcement(
    title: str = Form(...),
    content: str = Form(...),
    group_id: Optional[int] = Form(None),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.RoleEnum.TEACHER))
):
    file_paths = []
    
    if files:
        for file in files:
            if file.filename:
                saved_path = await save_file(file, current_user.id)
                file_paths.append(saved_path)
    
    announcement = models.Announcement(
        teacher_id=current_user.id,
        group_id=group_id,
        title=title,
        content=content,
        files=file_paths
    )
    
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    
    return announcement

@router.get("/", response_model=List[schemas.AnnouncementResponse])
def get_announcements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Announcement)
    
    # If student, only show their group or all groups
    if current_user.role == models.RoleEnum.STUDENT:
        query = query.filter(
            (models.Announcement.group_id == current_user.group_id) |
            (models.Announcement.group_id == None)
        )
    
    announcements = query.order_by(models.Announcement.created_at.desc()).all()
    
    result = []
    for a in announcements:
        result.append(schemas.AnnouncementResponse(
            id=a.id,
            teacher_name=a.teacher.full_name,
            group_name=a.group.name if a.group else "All Groups",
            title=a.title,
            content=a.content,
            files=a.files,
            created_at=a.created_at
        ))
    
    return result