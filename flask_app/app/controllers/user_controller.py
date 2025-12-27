

from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import and_
from ..models.seller import Seller
from ..models.contract import Contract
from flask import Blueprint, render_template, request, jsonify
from ..repositories.analytics_repository import AnalyticsRepository
from ..extensions import db

# user_bp = Blueprint("user", __name__, url_prefix="/user")
user_bp = Blueprint("user", __name__, url_prefix="/user")

def safe_to_str(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif value is None:
        return ""
    elif isinstance(value, float):
        import math
        if math.isnan(value):
            return ""
        return str(int(value)) if value.is_integer() else str(value)
    else:
        return str(value).strip().lower()

def parse_list_csv(csv_string):
    return set([safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)])

def parse_dynamic_filters(args):
    # Maps param names to contract column attributes
    filter_fields = [
        "status", "organization_type", "ministry", "department",
        "organization_name", "office_zone", "location", "buyer_designation",
        "buying_mode", "bid_number", "contract_date"
    ]
    filters = {}
    for field in filter_fields:
        value = args.get(field, None, type=str)
        if value:
            filters[field] = value.strip()
    min_total = args.get("min_total", None, type=float)
    max_total = args.get("max_total", None, type=float)
    if min_total is not None:
        filters["min_total"] = min_total
    if max_total is not None:
        filters["max_total"] = max_total
    return filters

def apply_contract_filters(query, filters):
    for field, value in filters.items():
        if field == "contract_date":
            try:
                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date == date_val)
            except Exception:
                continue
        elif field == "min_total":
            query = query.filter(Contract.total >= value)
        elif field == "max_total":
            query = query.filter(Contract.total <= value)
        else:
            column = getattr(Contract, field, None)
            if column is not None:
                query = query.filter(column.ilike(f"%{value}%"))
    return query

def contract_brand_match(contract, brand_set):
    contract_items = contract.items or []
    if not brand_set:
        return True
    for item in contract_items:
        brand = safe_to_str(item.get('brand', ''))
        if brand and brand in brand_set:
            return True
    return False

class Pagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page
        self.has_prev = page > 1
        self.has_next = (page * per_page) < total
        self.prev_num = page - 1
        self.next_num = page + 1

@user_bp.route("/contracts")
@login_required
def user_contracts():
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    # Subscription validation
    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    brand_set = parse_list_csv(current_user.brand_names)
    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    page = request.args.get('page', 1, type=int)
    per_page = 10

    filters = parse_dynamic_filters(request.args)
    base_query = Contract.query

    # Date range filter
    contract_date_param = request.args.get("contract_date", None, type=str)
    contract_date = None
    if contract_date_param:
        try:
            date_obj = datetime.strptime(contract_date_param, "%Y-%m-%d").date()
            if assigned_start and assigned_end and assigned_start <= date_obj <= assigned_end:
                contract_date = date_obj
                filters["contract_date"] = contract_date_param
        except Exception:
            contract_date = None

    if not contract_date:
        # Only fetch contracts within user's allowed range
        if assigned_start and assigned_end:
            base_query = base_query.filter(
                and_(
                    Contract.contract_date >= assigned_start,
                    Contract.contract_date <= assigned_end
                )
            )

    # Apply other dynamic filters
    base_query = apply_contract_filters(base_query, filters)

    # Order by contract_date DESC
    base_query = base_query.order_by(Contract.contract_date.desc())

    # Initial contracts (pre-brand filtering)
    contracts = base_query.all()
    
    # Brand filtering
    filtered_contracts = [c for c in contracts if contract_brand_match(c, brand_set)]

    total = len(filtered_contracts)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_contracts = filtered_contracts[start:end]

    pagination = Pagination(page, per_page, total)
    
    return render_template(
        "user_contract_info.html",
        contracts=paginated_contracts,
        pagination=pagination,
        user_brands=list(brand_set),
        assigned_start_date=assigned_start,
        assigned_end_date=assigned_end,
        filters_applied=filters
    )





                    


from flask import jsonify

@user_bp.route("/contract/api/<contract_id>")
@login_required
def contract_api(contract_id):
    contract = Contract.query.filter_by(contract_id=contract_id).first()
    print("contract", contract)
    if not contract:
        return jsonify({"error": "Contract not found"}), 404
    
    seller = Seller.query.filter_by(contract_no=contract.contract_id).first()
    print("seller",seller)
    contract_data = {
        "contract_id": contract.contract_id,
        "status": contract.status,
        "organization_name": contract.organization_name,
        "contract_date": contract.contract_date.strftime("%Y-%m-%d") if contract.contract_date else "",
        "total": contract.total,
        "items": contract.items or []
    }
    
    seller_data = None
    if seller:
        seller_data = {
            "company_name": seller.company_name,
            "seller_id": seller.seller_id,
            "contact_no": seller.contact_no,
            "email": seller.email,
            "address": seller.address,
            "msme_reg_no": seller.msme_reg_no,
            "gstin": seller.gstin
        }
    
    return jsonify({"contract": contract_data, "seller": seller_data})






from collections import Counter
from flask import request, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime

def safe_to_str(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif value is None:
        return ""
    elif isinstance(value, float):
        import math
        if math.isnan(value):
            return ""
        return str(int(value)) if value.is_integer() else str(value)
    else:
        return str(value).strip().lower()

def parse_list_csv(csv_string):
    return set([safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)])

def parse_seller_filters(args):
    filter_fields = [
        "company_name", "category_name", "gstin",
        "msme_reg_no", "email", "contact_no"
    ]
    filters = {}
    for field in filter_fields:
        value = args.get(field, None, type=str)
        if value:
            filters[field] = value.strip()
    return filters

def apply_seller_filters(query, filters):
    for field, value in filters.items():
        column = getattr(Seller, field, None)
        if column is not None:
            query = query.filter(column.ilike(f"%{value}%"))
    return query

class Pagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page
        self.has_prev = page > 1
        self.has_next = (page * per_page) < total
        self.prev_num = page - 1
        self.next_num = page + 1

@user_bp.route("/sellers")
@login_required
def user_sellers():
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    category_set = parse_list_csv(current_user.category_names)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    filters = parse_seller_filters(request.args)
    base_query = Seller.query
    base_query = apply_seller_filters(base_query, filters)

    # Apply allowed categories filter at database level
    if category_set:
        # Ensure case-insensitive matching
        base_query = base_query.filter(func.lower(Seller.category_name).in_(category_set))

    total = base_query.count()
    sellers = base_query.order_by(Seller.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    company_list = [s.company_name.strip() if s.company_name else '' for s in sellers]
    company_counts = Counter(company_list)
    
    unique_sellers = []
    
    for name, count in company_counts.items():
    
        # Pick one seller object (existing logic)
        seller_obj = next(
            (s for s in sellers if (s.company_name or '').strip() == name),
            None
        )
    
        if seller_obj:
            # 🔹 NEW: collect all contract_no for this company (same page, same filters)
            contract_nos = [
                s.contract_no
                for s in sellers
                if (s.company_name or '').strip() == name and s.contract_no
            ]
    
            unique_sellers.append({
                'company_name': name,
                'count': count,
                'seller': seller_obj,
                'contract_nos': contract_nos   # ✅ ADDED
            })
    # print(unique_sellers)
    pagination = Pagination(page, per_page, total)

    return render_template(
        "user_seller_info.html",
        sellers=sellers,
        unique_sellers=unique_sellers,
        pagination=pagination,
        user_categories=list(category_set),
        filters_applied=filters
    )

# from flask_wtf.csrf import csrf_exempt
import math

def sanitize_json(obj):
    """
    Recursively replace NaN with None (null in JSON)
    """
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj

from ..extensions import csrf
@user_bp.route("/api/contracts/by-contract-nos", methods=["POST"])
@login_required
@csrf.exempt
def get_contracts_by_contract_nos():

    #  SAME RESTRICTIONS AS /contracts
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    data = request.get_json()
    # print(data)
    contract_nos = data.get("contract_nos", [])
    # print(contract_nos)
    if not contract_nos or not isinstance(contract_nos, list):
        abort(400, "Invalid contract numbers")

    brand_set = parse_list_csv(current_user.brand_names)
    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    # ✅ Fetch contracts
    query = Contract.query.filter(Contract.contract_id.in_(contract_nos))
    # print(query)
    # Date range restriction
    if assigned_start and assigned_end:
        query = query.filter(
            Contract.contract_date.between(assigned_start, assigned_end)
        )

    contracts = query.order_by(Contract.contract_date.desc()).all()

    # Brand restriction (same logic you already use)
    def contract_brand_match(contract):
        for item in contract.items or []:
            if isinstance(item, dict):
                brand = safe_to_str(item.get("brand"))
                if brand and brand in brand_set:
                    return True
        return True

    filtered_contracts = [c for c in contracts if contract_brand_match(c)]

    # 🔄 Serialize
    return jsonify([
        {
            "contract_id": c.contract_id,
            "status": c.status,
            "organization_type": c.organization_type,
            "ministry": c.ministry,
            "department": c.department,
            "organization_name": c.organization_name,
            "office_zone": c.office_zone,
            "location": c.location,
            "buyer_designation": c.buyer_designation,
            "buying_mode": c.buying_mode,
            "bid_number": c.bid_number,
            "contract_date": c.contract_date.strftime("%Y-%m-%d") if c.contract_date else None,
            "total": c.total,
            "items": sanitize_json(c.items)
        }
        for c in filtered_contracts
    ])








@login_required
@user_bp.route("/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html", user=current_user)


from math import ceil
import json
from ..models.user import UserHistory

@user_bp.route("/profile")
@login_required
def profile():

    user = current_user

    # ---------------- PAGINATION CONFIG ----------------
    page = request.args.get("page", 1, type=int)
    per_page = 5

    query = UserHistory.query.filter_by(user_id=user.id)\
                             .order_by(UserHistory.changed_at.desc())

    total = query.count()
    history_rows = query.offset((page - 1) * per_page)\
                         .limit(per_page)\
                         .all()

    # Convert JSON snapshot → dict
    history = []
    for h in history_rows:
        history.append({
            "changed_at": h.changed_at,
            "snapshot": json.loads(h.data_snapshot)
        })

    pagination = {
        "page": page,
        "pages": ceil(total / per_page),
        "has_prev": page > 1,
        "has_next": page < ceil(total / per_page),
        "prev_num": page - 1,
        "next_num": page + 1
    }

    return render_template(
        "user_profile.html",
        user=user,
        history=history,
        pagination=pagination
    )



@user_bp.route("/sellers")
@login_required
def sellers():
    """Show current logged-in user's profile (read-only) chetan athore"""
    return render_template("user_seller_info.html", user=current_user)




# -------------------------------------------------------------------------
from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from app.repositories.analytics_repository import AnalyticsRepository
# from app.blueprints.user import user_bp
# from sqlalchemy import func, extract, or_


@user_bp.route("/analytics")
@login_required
def analytics():
    return render_template("user_analytics_info.html", user=current_user)


# -------------------------
# FILTER PARSER (FIXED)
# -------------------------
def parse_filters(args):
    filters = {
        "status": args.get("status") or None,
        "buying_mode": args.get("buying_mode") or None,
        "ministry": args.get("ministry") or None,
        "date_from": args.get("date_from") or None,
        "date_to": args.get("date_to") or None,
        "min_total": float(args["min_total"]) if args.get("min_total") else None,
        "max_total": float(args["max_total"]) if args.get("max_total") else None,
        'brands': args.getlist('brands[]')
    }

    # print("Filters received:", filters)
    return filters


# -------------------------
# ANALYTICS APIs
# -------------------------
@user_bp.route("/api/analytics/contracts_by_status")
def analytics_contracts_by_status():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_contracts_by_status(filters)
    return jsonify([{"status": r[0], "count": r[1]} for r in data])


@user_bp.route("/api/analytics/value_over_time")
def analytics_value_over_time():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_value_over_time(filters)
    return jsonify([{"date": r[0], "total": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/top_ministries")
def analytics_top_ministries():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_top_ministries(filters)
    return jsonify([{"ministry": r[0], "value": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/avg_by_buying_mode")
def analytics_avg_by_buying_mode():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_avg_by_buying_mode(filters)
    return jsonify([{"buying_mode": r[0], "avg_value": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/count_by_month")
def analytics_count_by_month():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_count_by_month(filters)
    return jsonify([
        {"year": int(r[0]), "month": int(r[1]), "count": r[2]}
        for r in data
    ])

# -----------------------------------------------------------------------------------
@user_bp.route('/user_compare_brand_info')
@login_required
def user_compare_brand_info():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_compare_brand_info.html", user=current_user)


@user_bp.route("/api/brands/user")
@login_required
def user_brands():
    print(current_user.brand_names)
    return jsonify(sorted(list(parse_list_csv(current_user.brand_names))))



@user_bp.route("/api/brands/select2")
@login_required
def brands_select2():
    term = request.args.get("term", "").lower()
    brands_set = set()

    contracts = Contract.query.all()
    for c in contracts:
        for item in c.items or []:
            if isinstance(item, dict):
                brand = safe_to_str(item.get("brand"))
                if brand:
                    brands_set.add(brand.upper())

    if term:
        brands = [b for b in brands_set if term in b.lower()]
    else:
        brands = list(brands_set)

    return jsonify([
        {"id": b, "text": b}
        for b in sorted(brands)
    ])




@user_bp.route("/api/analytics/brand-compare")
@login_required
def brand_compare():

    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    brand1 = request.args.get("brand1")
    brand2 = request.args.get("brand2")
    month = request.args.get("month")

    if not brand1 or not brand2 or not month:
        abort(400)

    # Validate user brand
    user_brand_set = parse_list_csv(current_user.brand_names)
    if brand1.lower() not in user_brand_set:
        abort(403)

    # Validate competitor exists
    brand_exists = False
    for c in Contract.query.all():
        for item in c.items or []:
            if isinstance(item, dict):
                b = safe_to_str(item.get("brand"))
                if b.lower() == brand2.lower():
                    brand_exists = True
                    break
        if brand_exists:
            break

    if not brand_exists:
        abort(404)

    return jsonify(
        AnalyticsRepository.compare_brands_monthwise(brand1, brand2, month)
    )

