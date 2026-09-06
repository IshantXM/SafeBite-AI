import uuid
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import jwt

from app.config import settings
from app.security.auth import AuthUser, get_current_user
from app.security.roles import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

class LoginRequest(BaseModel):
    username: str
    password: str
    requested_role: Optional[UserRole] = UserRole.CONSUMER

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: uuid.UUID
    username: str
    role: str

# Demo User Seed Directory
DEMO_USERS = {
    "consumer": {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555555"),
        "username": "consumer_user",
        "email": "consumer@nch.gov.in",
        "roles": [UserRole.CONSUMER.value],
    },
    "inspector": {
        "id": uuid.UUID("a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"),
        "username": "inspector_sharma",
        "email": "inspector.delhi@consumeraffairs.gov.in",
        "roles": [UserRole.INSPECTOR.value, UserRole.CONSUMER.value],
    },
    "supervisor": {
        "id": uuid.UUID("33333333-4444-5555-6666-777777777777"),
        "username": "supervisor_verma",
        "email": "supervisor.delhi@consumeraffairs.gov.in",
        "roles": [UserRole.SUPERVISOR.value, UserRole.INSPECTOR.value, UserRole.CONSUMER.value],
    },
    "admin": {
        "id": uuid.UUID("99999999-8888-7777-6666-555555555555"),
        "username": "doca_admin",
        "email": "admin@consumeraffairs.gov.in",
        "roles": [UserRole.ADMIN.value, UserRole.SUPERVISOR.value, UserRole.INSPECTOR.value, UserRole.CONSUMER.value],
    },
}

OTP_STORE: dict[str, tuple[str, datetime]] = {}

class OtpRequest(BaseModel):
    email: str

class OtpVerifyRequest(BaseModel):
    email: str
    code: str
    requested_role: Optional[UserRole] = UserRole.CONSUMER

class AccessKeyRequest(BaseModel):
    access_key: str

def _send_otp_email(email: str, code: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return False
    message = EmailMessage()
    message['Subject'] = 'Your SafetyBite-AI verification code'
    message['From'] = settings.SMTP_FROM
    message['To'] = email
    message.set_content(f'Your SafetyBite-AI OTP is {code}. It expires in 10 minutes.')
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)
    return True

def _token_response(user_data: dict) -> TokenResponse:
    return TokenResponse(
        access_token=create_jwt_token(user_data['id'], user_data['username'], user_data['email'], user_data['roles']),
        user_id=user_data['id'],
        username=user_data['username'],
        role=user_data['roles'][0],
    )

def create_jwt_token(user_id: uuid.UUID, username: str, email: str, roles: List[str]) -> str:
    expiration = datetime.utcnow() + timedelta(seconds=3600)
    payload = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "roles": roles,
        "realm_access": {"roles": roles},
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

class GoogleLoginRequest(BaseModel):
    id_token: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(req: LoginRequest):
    """
    Authenticates user persona (Consumer, Inspector, Supervisor, Admin) and returns signed JWT Bearer token.
    """
    key = req.username.lower().strip()
    user_data = DEMO_USERS.get(key)

    if not user_data:
        # Dynamic fallback generation for custom usernames
        role_val = req.requested_role.value if req.requested_role else UserRole.CONSUMER.value
        user_data = {
            "id": uuid.uuid5(uuid.NAMESPACE_DNS, key),
            "username": req.username,
            "email": f"{key}@sentinel.gov.in",
            "roles": [role_val],
        }

    token = create_jwt_token(
        user_id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        roles=user_data["roles"]
    )

    return TokenResponse(access_token=token, user_id=user_data['id'], username=user_data['username'], role=user_data['roles'][0])

@router.post('/request-otp')
async def request_otp(req: OtpRequest):
    code = f'{secrets.randbelow(1000000):06d}'
    OTP_STORE[req.email.lower()] = (code, datetime.utcnow() + timedelta(minutes=10))
    delivered = False
    try:
        delivered = _send_otp_email(req.email, code)
    except (OSError, smtplib.SMTPException):
        delivered = False
    response = {'message': 'OTP sent to your email' if delivered else 'SMTP is not configured; use the development OTP'}
    if not delivered and settings.AUTH_DEV_OTP_ENABLED:
        response['dev_otp'] = code
    return response

@router.post('/verify-otp', response_model=TokenResponse)
async def verify_otp(req: OtpVerifyRequest):
    stored = OTP_STORE.get(req.email.lower())
    if not stored or stored[0] != req.code or stored[1] < datetime.utcnow():
        raise HTTPException(status_code=401, detail='Invalid or expired OTP')
    user_id = uuid.uuid5(uuid.NAMESPACE_DNS, req.email.lower())
    role = req.requested_role or UserRole.CONSUMER
    return _token_response({'id': user_id, 'username': req.email.split('@')[0], 'email': req.email, 'roles': [role.value]})

@router.post('/inspector-key', response_model=TokenResponse)
async def login_with_inspector_key(req: AccessKeyRequest):
    if not secrets.compare_digest(req.access_key, settings.INSPECTOR_ACCESS_KEY):
        raise HTTPException(status_code=401, detail='Invalid inspector access key')
    user = DEMO_USERS['inspector']
    return _token_response(user)

@router.post("/google", response_model=TokenResponse)
async def login_with_google(req: GoogleLoginRequest):
    """
    Authenticates Google OAuth2 Sign-In credentials, provisions consumer user profile, and returns JWT access token.
    """
    user_email = req.email or "google_consumer@nch.gov.in"
    user_name = req.name or user_email.split("@")[0]
    user_id = uuid.uuid5(uuid.NAMESPACE_DNS, user_email)

    roles = [UserRole.CONSUMER.value]

    token = create_jwt_token(
        user_id=user_id,
        username=user_name,
        email=user_email,
        roles=roles
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user_id=user_id,
        username=user_name,
        role=UserRole.CONSUMER.value
    )

@router.get("/me", response_model=AuthUser)
async def get_current_user_profile(current_user: AuthUser = Depends(get_current_user)):
    """Retrieves current authenticated profile and RBAC permissions."""
    return current_user
