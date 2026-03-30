import os
import shutil
from fastapi import UploadFile
from typing import List
import aiofiles
from app.config import settings

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

async def save_file(file: UploadFile, user_id: int):
    """Save uploaded file and return its path"""
    filename = f"user_{user_id}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_path

async def check_total_size(files: List[UploadFile]) -> int:
    """Calculate total size of all files"""
    total = 0
    for file in files:
        content = await file.read()
        total += len(content)
        await file.seek(0)  # Reset file pointer for later reading
    return total

def delete_file(file_path: str):
    """Delete a file"""
    if os.path.exists(file_path):
        os.remove(file_path)
