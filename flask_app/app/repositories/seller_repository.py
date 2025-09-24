from ..extensions import db
from ..models.seller import Seller
import pandas as pd

def parse_value(value, target_type=str):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if target_type == str:
        if isinstance(value, str) and value.strip() == "":
            return None
        return str(value)
    if target_type == 'datetime':
        try:
            dt = pd.to_datetime(value, errors='coerce')
            if pd.isna(dt):
                return None
            return dt.to_pydatetime()
        except Exception:
            return None
    return value

def get_sellers_filtered_paginated(filters, page=1, per_page=50):
    query = Seller.query
    for field in ['contract_no', 'category_name', 'seller_id', 'company_name', 'contact_no', 'email', 'msme_reg_no', 'gstin']:
        val = filters.get(field)
        if val:
            col = getattr(Seller, field)
            query = query.filter(col.ilike(f"%{val}%"))
    if filters.get('generated_date'):
        query = query.filter(Seller.generated_date == filters['generated_date'])
    return query.order_by(Seller.generated_date.desc()).paginate(page=page, per_page=per_page)

def add_or_update_seller(data):
    contract_no = parse_value(data.get('contract_no'), str)
    seller = Seller.query.filter_by(contract_no=contract_no).first()
    values = dict(
        generated_date=parse_value(data.get('generated_date'), 'datetime'),
        category_name=parse_value(data.get('category_name'), str),
        seller_id=parse_value(data.get('seller_id'), str),
        company_name=parse_value(data.get('company_name'), str),
        contact_no=parse_value(data.get('contact_no'), str),
        email=parse_value(data.get('email'), str),
        address=parse_value(data.get('address'), str),
        msme_reg_no=parse_value(data.get('msme_reg_no'), str),
        gstin=parse_value(data.get('gstin'), str)
    )
    if seller:
        for k, v in values.items():
            setattr(seller, k, v)
        db.session.commit()
        return True
    seller = Seller(contract_no=contract_no, **values)
    db.session.add(seller)
    db.session.commit()
    return True

def bulk_delete_sellers(ids):
    if not ids:
        return 0
    count = Seller.query.filter(Seller.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return count
