from pydantic import BaseModel, EmailStr, Field, model_validator


class UserRegisterSchema(BaseModel):
    email: EmailStr = Field(..., description="Email of the user")
    password: str = Field(..., description="Password of the user")
    confirm_password: str

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description="Email of the user")
    password: str = Field(..., description="Password of the user")



class UserForgotPasswordSchema(BaseModel):
    email: EmailStr = Field(..., description="Email of the user")


class UserResetPasswordSchema(BaseModel):
    password: str = Field(..., description="Password of the user")
    confirm_password: str

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self