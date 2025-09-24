from ..extensions import db

class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    product_count = db.Column(db.Integer)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Brand {self.code}>"
