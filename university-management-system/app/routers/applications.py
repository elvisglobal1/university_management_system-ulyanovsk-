from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from app import models, schemas, auth
from app.database import get_db
from app.config import settings
from app.services.file_service import save_file, check_total_size

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.post("/create")
async def create_application(
    type: str = Form(...),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if current_user.role != models.RoleEnum.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can create applications")
    
    # Check total size
    file_paths = []
    total_size = 0
    
    if files:
        total_size = await check_total_size(files)
        if total_size > settings.max_upload_size:
            raise HTTPException(status_code=400, detail=f"Total file size exceeds {settings.max_upload_size / 1024 / 1024} MB limit")
        
        for file in files:
            if file.filename:
                ext = os.path.splitext(file.filename)[1].lower()
                if ext not in ['.pdf', '.doc', '.jpg', '.jpeg', '.png']:
                    raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")
                
                saved_path = await save_file(file, current_user.id)
                file_paths.append(saved_path)
    
    application = models.Application(
        user_id=current_user.id,
        type=models.ApplicationTypeEnum(type),
        description=description,
        files=file_paths,
        total_size=total_size
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application

@router.get("/my", response_model=List[schemas.ApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    applications = db.query(models.Application).filter(
        models.Application.user_id == current_user.id
    ).all()
    
    return applications
