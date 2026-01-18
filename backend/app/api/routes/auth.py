from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, settings
# from app.services.user_service import authenticate_user # To be implemented

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login padrão OAuth2.
    Para fins de hardening enterprise, este endpoint validará contra o Supabase.
    """
    # MOCK AUTH FOR INITIAL HARDENING (Replace with real Supabase Auth later)
    # Em um sistema real, aqui buscaríamos o usuário no Supabase
    if form_data.username == "admin" and form_data.password == "admin123":
        user_id = "00000000-0000-0000-0000-000000000000" # Admin UUID
    else:
        # Aqui viria a lógica real de autenticação
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
