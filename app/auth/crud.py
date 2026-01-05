from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.orm import Session
from app.db.models.user import User

def get_user_by_id(db: Session, user_id: str):
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    else:
        return JSONResponse(content="User not found", status_code=status.HTTP_404_NOT_FOUND)