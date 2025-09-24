from ..extensions import db
from ..models.contract import Contract
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
    if target_type == float:
        try:
            return float(value)
        except:
            return None
    if target_type == 'datetime':
        try:
            dt = pd.to_datetime(value, errors='coerce')
            if pd.isna(dt):
                return None
            return dt.to_pydatetime()
        except:
            return None
    return value

def get_unique_items(items):
    seen = set()
    unique_items = []
    for item in items:
        raw_service = item.get('service')
        raw_product = item.get('product')

        def clean_key(value):
            if isinstance(value, str):
                return value.strip().lower()
            elif value is None or (isinstance(value, float) and pd.isna(value)):
                return ''
            else:
                return str(value).strip().lower()

        service_key = clean_key(raw_service)
        product_key = clean_key(raw_product)

        # Use service_key if present, else product_key as uniqueness key
        unique_key = service_key or product_key

        if unique_key and unique_key not in seen:
            seen.add(unique_key)
            unique_items.append(item)

    return unique_items

def get_contracts_filtered_paginated(filters, page=1, per_page=50):
    query = Contract.query
    for field in ['status', 'organization_type', 'ministry', 'department', 'organization_name',
                  'office_zone', 'location', 'buyer_designation', 'buying_mode', 'bid_number',
                  'contract_date', 'total', 'contract_id']:
        val = filters.get(field)
        if val:
            col = getattr(Contract, field)
            if field in ['contract_date', 'total']:
                query = query.filter(col == val)
            else:
                query = query.filter(col.ilike(f"%{val}%"))
    return query.order_by(Contract.contract_date.desc()).paginate(page=page, per_page=per_page)

def add_contract(contract_data):
    contract_id = parse_value(contract_data.get('contract_id'), str)
    contract = Contract.query.filter_by(contract_id=contract_id).first()
    items = contract_data.get('items', [])
    unique_items = get_unique_items(items)

    if contract:
        existing_items = contract.items or []
        contract.items = get_unique_items(existing_items + unique_items)
        db.session.commit()
        return True

    contract = Contract(
        contract_id=contract_id,
        status=parse_value(contract_data.get('status'), str),
        organization_type=parse_value(contract_data.get('organization_type'), str),
        ministry=parse_value(contract_data.get('ministry'), str),
        department=parse_value(contract_data.get('department'), str),
        organization_name=parse_value(contract_data.get('organization_name'), str),
        office_zone=parse_value(contract_data.get('office_zone'), str),
        location=parse_value(contract_data.get('location'), str),
        buyer_designation=parse_value(contract_data.get('buyer_designation'), str),
        buying_mode=parse_value(contract_data.get('buying_mode'), str),
        bid_number=parse_value(contract_data.get('bid_number'), str),
        contract_date=parse_value(contract_data.get('contract_date'), 'datetime'),
        total=parse_value(contract_data.get('total'), float),
        items=unique_items
    )
    db.session.add(contract)
    db.session.commit()
    return True

def bulk_delete(contract_ids):
    if not contract_ids:
        return 0
    count = Contract.query.filter(Contract.id.in_(contract_ids)).delete(synchronize_session=False)
    db.session.commit()
    return count








def get_contracts_filtered_paginated_user(filters, page=1, per_page=50):
    query = Contract.query

    # Apply generic filters
    for field in ['status', 'organization_type', 'ministry', 'department', 'organization_name',
                  'office_zone', 'location', 'buyer_designation', 'buying_mode', 'bid_number',
                  'contract_id']:
        val = filters.get(field)
        if val:
            col = getattr(Contract, field)
            query = query.filter(col.ilike(f"%{val}%"))

    # Filter by contract_date if precise date given
    contract_date = filters.get('contract_date')
    if contract_date:
        query = query.filter(Contract.contract_date == contract_date)

    # Filter by category_names list (assumed Contract.items contains category_name)
    category_names = filters.get('category_names')
    if category_names:
        # Filter contracts having at least one item with category_name in list
        query = query.filter(
            Contract.items.op('jsonb_path_exists')(
                f"$[*] ? (@.category_name in {category_names})"
            )
        )

    # Filter by brand_names list (assumed Contract.items contains brand)
    brand_names = filters.get('brand_names')
    if brand_names:
        query = query.filter(
            Contract.items.op('jsonb_path_exists')(
                f"$[*] ? (@.brand in {brand_names})"
            )
        )

    return query.order_by(Contract.contract_date.desc()).paginate(page=page, per_page=per_page)

