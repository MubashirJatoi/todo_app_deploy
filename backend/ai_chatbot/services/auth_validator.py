from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from ai_chatbot.config import config
import uuid


class AuthValidator:
    """
    Service class to validate authentication for AI chatbot endpoints
    """

    def __init__(self):
        self.security = HTTPBearer()
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM

    async def get_current_user_id(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> uuid.UUID:
        """
        Validate JWT token and extract user ID
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            token = credentials.credentials
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")

            if user_id is None:
                raise credentials_exception

            return uuid.UUID(user_id)
        except JWTError:
            raise credentials_exception
        except Exception:
            raise credentials_exception

    def validate_token(self, token: str) -> Optional[uuid.UUID]:
        """
        Validate a JWT token and return the user ID if valid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")

            if user_id is None:
                return None

            return uuid.UUID(user_id)
        except JWTError:
            return None
        except Exception:
            return None

    def is_valid_user(self, user_id: uuid.UUID) -> bool:
        """
        Check if the user ID is valid (in a real implementation, you'd check against the database)
        For now, just verify it's a valid UUID
        """
        try:
            # In a real implementation, you'd check if the user exists in the database
            # For now, just ensure it's a valid UUID
            return user_id is not None
        except Exception:
            return False


# Global instance for reuse
auth_validator = AuthValidator()