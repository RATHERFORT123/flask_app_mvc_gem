from ..extensions import db
from ..models.contract import Contract
from ..models.brand import Brand


def normalize_brand(name: str) -> str:
    return (
        name.strip()
        .upper()
        .replace("™", "")
        .replace("®", "")
    )


def sync_brands_from_contracts():
    # 1️⃣ Get existing brand names
    existing = {
        b.name.upper()
        for b in db.session.query(Brand.name).all()
    }

    # 2️⃣ Extract brands from contracts JSON
    found = set()

    contracts = db.session.query(Contract.items).all()
    for (items,) in contracts:
        if not items:
            continue
        for item in items:
            if isinstance(item, dict):
                brand = item.get("brand")
                if brand:
                    found.add(normalize_brand(brand))

    # 3️⃣ Insert only new brands
    inserted = 0
    for brand_name in found - existing:
        db.session.add(
            Brand(
                code=brand_name[:200],   # auto code
                name=brand_name,
                product_count=0
            )
        )
        inserted += 1

    db.session.commit()
    return len(found), inserted
