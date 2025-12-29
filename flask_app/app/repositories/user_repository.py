


from typing import Optional
from ..extensions import db
from ..models.user import User, UserHistory
from datetime import datetime
import json

def _unique_comma_separated(s):
    if not s:
        return ""
    items = [item.strip() for item in s.split(',') if item.strip()]
    unique = []
    seen = set()
    for i in items:
        li = i.lower()
        if li not in seen:
            unique.append(i)
            seen.add(li)
    return ",".join(unique)

def save_user_history(user: User):
    snapshot = {
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "is_blocked": user.is_blocked,
        "address": user.address,
        "number": user.number,
        "comment": user.comment,
        "category_names": user.category_names,
        "brand_names": user.brand_names,
        "assigned_date_range_start": user.assigned_date_range_start.isoformat() if user.assigned_date_range_start else None,
        "assigned_date_range_end": user.assigned_date_range_end.isoformat() if user.assigned_date_range_end else None,
        "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None,
        "amount": user.amount,
        "payment_status": user.payment_status,
        "subscription_plan": user.subscription_plan,
    }
    history = UserHistory(user_id=user.id, data_snapshot=json.dumps(snapshot))
    db.session.add(history)
    # db.session.commit()


def get_by_id(user_id: int) -> Optional[User]:
    return User.query.get(user_id)


def get_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email.strip().lower()).first()


def get_all() -> list[User]:
    return User.query.order_by(User.username).all()


def create_user(username: str, email: str, password: str, is_admin: bool=False, is_verified: bool=False, is_blocked: bool=False,
                address: str = None, number: str = None, comment: str = None,
                category_names: str = None, brand_names: str = None,
                assigned_date_range_start=None, assigned_date_range_end=None, subscription_date=None,
                amount=None, payment_status=None, subscription_plan=None) -> User:
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        is_admin=is_admin,
        is_verified=is_verified,
        is_blocked=is_blocked,
        address=address,
        number=number,
        comment=comment,
        category_names=_unique_comma_separated(category_names),
        brand_names=_unique_comma_separated(brand_names),
        assigned_date_range_start=assigned_date_range_start,
        assigned_date_range_end=assigned_date_range_end,
        subscription_date=subscription_date,
        amount=amount,
        payment_status=payment_status,
        subscription_plan=subscription_plan
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def update_user(
    u: User,
    username: str,
    email: str,
    password: str | None,
    is_admin: bool,
    is_verified: bool,
    is_blocked: bool,
    address: str = None,
    number: str = None,
    comment: str = None,
    category_names: str = None,
    brand_names: str = None,
    assigned_date_range_start=None,
    assigned_date_range_end=None,
    subscription_date=None,
    amount=None,
    payment_status=None,
    subscription_plan=None
) -> User:
    try:
        save_user_history(u)

        u.username = username.strip()
        u.email = email.strip().lower()

        if password:
            u.set_password(password)

        u.is_admin = is_admin
        u.is_verified = is_verified
        u.is_blocked = is_blocked
        u.address = address
        u.number = number
        u.comment = comment
        u.category_names = _unique_comma_separated(category_names)
        u.brand_names = _unique_comma_separated(brand_names)
        u.assigned_date_range_start = assigned_date_range_start
        u.assigned_date_range_end = assigned_date_range_end
        u.subscription_date = subscription_date
        u.amount = amount
        u.payment_status = payment_status
        u.subscription_plan = subscription_plan

        db.session.commit()
        return u

    except Exception as e:
        db.session.rollback()   # 🔥 THIS IS THE KEY
        raise

# def update_user(u: User, username: str, email: str, password: str | None, is_admin: bool, is_verified: bool, is_blocked: bool,
#                 address: str = None, number: str = None, comment: str = None,
#                 category_names: str = None, brand_names: str = None,
#                 assigned_date_range_start=None, assigned_date_range_end=None, subscription_date=None,
#                 amount=None, payment_status=None, subscription_plan=None) -> User:
#     save_user_history(u)

#     u.username = username.strip()
#     u.email = email.strip().lower()
#     if password:
#         u.set_password(password)
#     u.is_admin = is_admin
#     u.is_verified = is_verified
#     u.is_blocked = is_blocked
#     u.address = address
#     u.number = number
#     u.comment = comment
#     u.category_names = _unique_comma_separated(category_names)
#     u.brand_names = _unique_comma_separated(brand_names)
#     u.assigned_date_range_start = assigned_date_range_start
#     u.assigned_date_range_end = assigned_date_range_end
#     u.subscription_date = subscription_date
#     u.amount = amount
#     u.payment_status = payment_status
#     u.subscription_plan = subscription_plan
#     db.session.commit()
#     return u


def delete_user(u: User) -> None:
    db.session.delete(u)
    db.session.commit()
