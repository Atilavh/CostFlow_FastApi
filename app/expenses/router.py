from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.expenses.schema import CreateCategorySchema, UserCategoriesSchema
from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.expenses.service import create_category_service, get_user_categories, delete_category_service
from typing import List
from uuid import UUID





router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post('/create_category', response_model=UserCategoriesSchema, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CreateCategorySchema, 
    db:Session = Depends(get_db), 
    user:User = Depends(get_current_user)):
    return create_category_service(db, data.name, user)
    

@router.delete('/delete_category/{category_id}', status_code=status.HTTP_200_OK)
def delete_category(
    category_id: UUID,
    db:Session = Depends(get_db), 
    user:User = Depends(get_current_user)):
    return delete_category_service(category_id, db, user)


@router.get("/get_categories_of_user", response_model=List[UserCategoriesSchema], status_code=status.HTTP_200_OK)
def get_cat(user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    return get_user_categories(db, user)