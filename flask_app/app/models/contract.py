from sqlalchemy.dialects.postgresql import JSON
from ..extensions import db

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(100))
    organization_type = db.Column(db.String(100))
    ministry = db.Column(db.String(255))
    department = db.Column(db.String(255))
    organization_name = db.Column(db.String(255))
    office_zone = db.Column(db.String(100))
    location = db.Column(db.String(255))
    buyer_designation = db.Column(db.String(100))
    buying_mode = db.Column(db.String(100))
    bid_number = db.Column(db.String(100))
    contract_date = db.Column(db.DateTime)
    total = db.Column(db.Float)
    items = db.Column(JSON)  # JSON array of item dicts
