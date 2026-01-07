from app.db.models.user import User
from app.db.models.exceptions import Category
from sqlalchemy.orm import Session
from slugify import slugify
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def create_category_service(db: Session, name: str, user: User):
    category = Category(
        name=name,
        slug=slugify(name),
        user_id=user.id,
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_category_service(category_id: int, db: Session, user: User):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return JSONResponse(content="Category deleted successfully", status_code=status.HTTP_200_OK)

def get_user_categories(db: Session, user: User):
    return db.query(Category).filter(Category.user_id == user.id, Category.is_active == True).all()