from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.services.email_service import generate_password, send_email
import random
import string

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(models.User).filter(
        models.User.login == user_data.login
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    
    # Generate password
    generated_password = generate_password()
    password_hash = auth.get_password_hash(generated_password)
    
    # Create user
    db_user = models.User(
        login=user_data.login,
        password_hash=password_hash,
        email=user_data.email,
        full_name=user_data.full_name,
        group_id=user_data.group_id,
        role=models.RoleEnum.STUDENT
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send password via email (simulated)
    send_email(user_data.email, generated_password)
    
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.login, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )
    
    access_token = auth.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/reset-password")
def reset_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.login == request.login,
        models.User.email == request.email
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_password = generate_password()
    user.password_hash = auth.get_password_hash(new_password)
    db.commit()
    
    send_email(user.email, new_password)
    
    return {"message": "New password sent to your email"}