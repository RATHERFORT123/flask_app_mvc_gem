# from flask_login import UserMixin
# from ..extensions import db
# from datetime import datetime

# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128))
#     is_admin = db.Column(db.Boolean, default=False)
#     is_verified = db.Column(db.Boolean, default=False)
#     is_blocked = db.Column(db.Boolean, default=False)
#     address = db.Column(db.String(255), nullable=True)
#     number = db.Column(db.String(50), nullable=True)
#     comment = db.Column(db.Text, nullable=True)

#     category_names = db.Column(db.Text, nullable=True)
#     brand_names = db.Column(db.Text, nullable=True)

#     assigned_date_range_start = db.Column(db.Date, nullable=True)
#     assigned_date_range_end = db.Column(db.Date, nullable=True)
#     subscription_date = db.Column(db.Date, nullable=True)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def set_password(self, password):
#         from werkzeug.security import generate_password_hash
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         from werkzeug.security import check_password_hash
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f"<User {self.username}>"






from flask_login import UserMixin
from ..extensions import db
from datetime import datetime
from sqlalchemy import Float

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    category_names = db.Column(db.Text, nullable=True)  # Comma-separated categories
    brand_names = db.Column(db.Text, nullable=True)     # Comma-separated brands
    assigned_date_range_start = db.Column(db.Date, nullable=True)
    assigned_date_range_end = db.Column(db.Date, nullable=True)
    subscription_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # New fields
    amount = db.Column(Float, nullable=True)
    payment_status = db.Column(db.String(50), nullable=True)
    subscription_plan = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class UserHistory(db.Model):
    __tablename__ = "user_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    data_snapshot = db.Column(db.Text, nullable=False)  # JSON string snapshot of user state
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
