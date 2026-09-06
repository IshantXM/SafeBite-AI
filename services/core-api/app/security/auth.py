import uuid
from typing import Any, Dict, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import jwt

from app.config import settings
from app.security.roles import UserRole

security_scheme = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    id: uuid.UUID
    username: str
    email: Optional[str] = None
    roles: List[str] = []


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes Keycloak JWT token or local HMAC signature."""
    try:
        # First try Keycloak public key if available
        if settings.KEYCLOAK_PUBLIC_KEY:
            formatted_key = f"-----BEGIN PUBLIC KEY-----\n{settings.KEYCLOAK_PUBLIC_KEY}\n-----END PUBLIC KEY-----"
            payload = jwt.decode(token, formatted_key, algorithms=["RS256"], options={"verify_aud": False})
            return payload
    except Exception:
        pass

    # Fallback / Local HMAC validation
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> AuthUser:
    """Authenticates the Bearer token and returns the current user context."""
    if not credentials:
        # For seamless local development/inspection demo without active Keycloak instance
        # Return standard DOCA Inspector identity
        return AuthUser(
            id=uuid.UUID("a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"),
            username="doca_field_inspector_01",
            email="inspector.delhi@consumeraffairs.gov.in",
            roles=[UserRole.INSPECTOR, UserRole.SUPERVISOR, UserRole.ADMIN]
        )

    token = credentials.credentials
    payload = decode_token(token)

    # Extract user identity from Keycloak or standard JWT
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject identifier")

    try:
        user_uuid = uuid.UUID(sub)
    except ValueError:
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, sub)

    # Extract roles from Keycloak realm_access or custom roles claim
    roles = []
    if "realm_access" in payload and "roles" in payload["realm_access"]:
        roles.extend(payload["realm_access"]["roles"])
    if "roles" in payload:
        roles.extend(payload["roles"])

    return AuthUser(
        id=user_uuid,
        username=payload.get("preferred_username", payload.get("username", "doca_user")),
        email=payload.get("email"),
        roles=roles
    )


def require_roles(required_roles: List[UserRole]):
    """Enforces role-based access control (RBAC)."""
    async def role_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        user_roles = [r.lower() for r in current_user.roles]
        required_role_strings = [r.value.lower() for r in required_roles]
        
        # Check if user has any of the required roles or is Admin
        if "admin" in user_roles or any(r in user_roles for r in required_role_strings):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation requires one of the following roles: {[r.value for r in required_roles]}"
        )
    return role_checker
