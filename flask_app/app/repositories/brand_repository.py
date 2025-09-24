import pandas as pd
from ..extensions import db
from ..models.brand import Brand


def get_all_brands():
    return Brand.query.order_by(Brand.id).all()

def add_brand(code, product_count, name):
    try:
        # Handle NaN values before creating brand
        if pd.isna(name) or str(name).lower() == 'nan':
            name = 'Unknown Brand'
        if pd.isna(code) or str(code).lower() == 'nan':
            code = 'Unknown Code'
        if pd.isna(product_count):
            product_count = 0
            
        # Check if brand already exists
        if Brand.query.filter_by(code=code).first():
            return False
            
        brand = Brand(code=code, product_count=product_count, name=name)
        db.session.add(brand)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False


def update_brand(brand_id, code, product_count, name):
    brand = Brand.query.get(brand_id)
    if brand:
        brand.code = code
        brand.product_count = product_count
        brand.name = name
        db.session.commit()
        return True
    return False

def delete_brand(brand_id):
    brand = Brand.query.get(brand_id)
    if brand:
        db.session.delete(brand)
        db.session.commit()
        return True
    return False
