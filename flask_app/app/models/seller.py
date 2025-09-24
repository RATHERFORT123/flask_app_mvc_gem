from ..extensions import db

class Seller(db.Model):
    __tablename__ = 'sellers'
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(255), unique=True, nullable=False)
    generated_date = db.Column(db.DateTime)
    category_name = db.Column(db.String(255))
    seller_id = db.Column(db.String(100))
    company_name = db.Column(db.String(255))
    contact_no = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    msme_reg_no = db.Column(db.String(100))
    gstin = db.Column(db.String(100))
