from typing import Optional
from ..repositories.user_repository import get_by_email, create_user
from ..models.user import User

def authenticate(email: str, password: str) -> Optional[User]:
    user = get_by_email(email)
    if user and not user.is_blocked and user.check_password(password):
        return user
    return None

def register(username: str, email: str, password: str,
             address: str = None, number: str = None) -> User:
    return create_user(
        username=username,
        email=email,
        password=password,
        is_admin=False,
        is_verified=False,
        is_blocked=False,
        address=address,
        number=number
    )


