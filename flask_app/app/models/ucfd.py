from sqlalchemy.dialects.postgresql import JSON
from ..extensions import db
from sqlalchemy.schema import UniqueConstraint

class UCFD(db.Model):
    __tablename__ = 'ucfd'
    id = db.Column(db.Integer, primary_key=True)

    # Contract fields
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

    # Item fields
    service = db.Column(db.String(512))
    product = db.Column(db.String(255))
    brand = db.Column(db.String(255))
    model = db.Column(db.String(255))
    hsn_code = db.Column(db.String(100))
    ordered_quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    # Seller fields
    generated_date = db.Column(db.DateTime)
    category_name = db.Column(db.String(255))
    seller_id = db.Column(db.String(100))
    company_name = db.Column(db.String(255))
    contact_no = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    msme_reg_no = db.Column(db.String(100))
    gstin = db.Column(db.String(100))

    __table_args__ = (
        UniqueConstraint(
            'status', 'organization_type', 'ministry', 'department', 'organization_name',
            'office_zone', 'location', 'buyer_designation', 'buying_mode', 'bid_number',
            'contract_date', 'total', 'service', 'product', 'brand', 'model', 'hsn_code',
            'ordered_quantity', 'price', 'generated_date', 'category_name', 'seller_id',
            'company_name', 'contact_no', 'email', 'address', 'msme_reg_no', 'gstin',
            name='ucfd_unique_combo'
        ),
    )
