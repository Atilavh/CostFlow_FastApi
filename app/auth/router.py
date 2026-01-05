import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.schema import UserRegisterSchema, UserLoginSchema, UserForgotPasswordSchema, UserResetPasswordSchema
from app.auth.service import register_user, get_user_by_email
from app.core.security import generate_access_token, generate_refresh_token, refresh_access_token, get_current_user, verify_access_token, hash_password
from app.db.models.user import RefreshToken, User, PasswordResetToken
from datetime import datetime, timedelta
from app.utils.smtp import send_mail

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterSchema, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    user = register_user(db, data.email, data.password)
    
    return {
        "id": user.id,
        "email": user.email,
        "message": "User registered successfully"
    }

@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: UserLoginSchema, db: Session = Depends(get_db), response: Response = None):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    token_data = {"sub": str(user.id)}
    access_token = generate_access_token(token_data)
    refresh_token = generate_refresh_token(token_data)
    db.add(
        RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expire_at=datetime.utcnow() + timedelta(days=7)
        )
    )
    db.commit()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/",
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=7*24*60*60
    )


    return {
        "access_token": access_token,
        "message": "User logged in successfully"
    }



@router.post('/forgot_password', status_code=status.HTTP_200_OK)
def forgot_password(data: UserForgotPasswordSchema, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        return JSONResponse(
            content="User dose not exist", status_code=status.HTTP_404_NOT_FOUND
        )
    token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id = user.id,
        token = token,
        expire_at = datetime.utcnow() + timedelta(minutes=15)
    )

    db.add(reset_token)
    db.commit()


    reset_link = f"https:127.0.0.1/reset-password?token={token}"
    send_mail(
        to = user.email,
        subject = "Reset your password",
        body = f"Click here to reset password: {reset_link}"
    )
    return JSONResponse(content="Password reset link sent to your email", status_code=status.HTTP_200_OK)


@router.get('/reset_password', status_code=status.HTTP_200_OK)
def validate_reset_token(token: str, db: Session = Depends(get_db)):
    token_obj = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.expire_at > datetime.utcnow(),
        PasswordResetToken.used == False
    ).first()

    if not token_obj:
        return JSONResponse(content={
                "message": "Invalid token or token expired",
                "error": True
            },
            status_code=status.HTTP_400_BAD_REQUEST)
        
    return JSONResponse(content="Token is valid", status_code=status.HTTP_200_OK)


@router.post('/reset_password', status_code=status.HTTP_200_OK)
def reset_password(data: UserResetPasswordSchema, db: Session = Depends(get_db)):
    token_obj = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.expire_at > datetime.utcnow(),
        PasswordResetToken.used == False
    ).first()

    if not token_obj:
        return JSONResponse(content={
                "message": "Invalid token or token expired",
                "error": True
            },
            status_code=status.HTTP_400_BAD_REQUEST)
        
    user = db.query(User).get(token_obj.user_id)
    user.password = hash_password(data.password)
    token_obj.used = True

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoke == False
    ).update({"revoke": True})
    db.commit()

    return JSONResponse(content="Password reset successfully", status_code=status.HTTP_200_OK)

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, refresh_token: str = Cookie(None), db:Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    token_obj = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.revoke == False
    ).first()

    if token_obj:
        token_obj.revoke = True
        db.commit()

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=False,
        samesite="strict"
    )
    return response

@router.get("/refresh", status_code=status.HTTP_200_OK)
def re_get_access_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    return refresh_access_token(refresh_token)

@router.get('/me')
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }