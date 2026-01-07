import uuid
from pydantic import BaseModel, Field


class CreateCategorySchema(BaseModel):
    name: str = Field(..., description="Name of the category")


class UserCategoriesSchema(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool

    class Config:
        from_attributes = True