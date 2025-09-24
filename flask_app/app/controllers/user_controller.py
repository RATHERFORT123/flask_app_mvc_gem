from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from datetime import datetime
from ..models.contract import Contract

from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from datetime import datetime
from ..models.contract import Contract

user_bp = Blueprint("user", __name__, url_prefix="/user")

def safe_to_str(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif value is None:
        return ""
    elif isinstance(value, float):
        try:
            import math
            if math.isnan(value):
                return ""
        except Exception:
            pass
        return str(int(value)) if value.is_integer() else str(value)
    else:
        return str(value).strip().lower()

def parse_list_csv(csv_string):
    return set([safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)])

@login_required
@user_bp.route("/contracts")
def user_contracts():
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    user_categories = parse_list_csv(current_user.category_names)
    user_brands = parse_list_csv(current_user.brand_names)
    assigned_start_date = current_user.assigned_date_range_start
    assigned_end_date = current_user.assigned_date_range_end
    subscription_date = current_user.subscription_date

    if not subscription_date or subscription_date < datetime.utcnow().date():
        abort(403)
    
    input_date_str = request.args.get('contract_date', type=str)
    contract_date = None
    if input_date_str:
        try:
            dt = datetime.strptime(input_date_str, "%Y-%m-%d").date()
            if assigned_start_date and assigned_end_date and assigned_start_date <= dt <= assigned_end_date:
                contract_date = dt
        except Exception:
            contract_date = None

    all_contracts = Contract.query.order_by(Contract.contract_date.desc()).all()
    filtered_contracts = []

    print("user_categories:", user_categories)
    print("user_brands:", user_brands)
    print("contract_date filter:", contract_date)
    print("assigned start date:", assigned_start_date)
    print("assigned end date:", assigned_end_date)

    for contract in all_contracts:
        if contract_date:
            if not contract.contract_date or contract.contract_date.date() != contract_date:
                continue
        elif assigned_start_date and assigned_end_date:
            if not contract.contract_date or not (assigned_start_date <= contract.contract_date.date() <= assigned_end_date):
                continue

        contract_items = contract.items or []

        has_category = True if not user_categories else False
        has_brand = True if not user_brands else False

        for item in contract_items:
            cat = safe_to_str(item.get('category_name', ''))
            brand = safe_to_str(item.get('brand', ''))
            if user_categories and cat in user_categories:
                has_category = True
            if user_brands and brand in user_brands:
                has_brand = True
        
        print(f"Checking contract {contract.contract_id}: has_category={has_category}, has_brand={has_brand}")

        if has_category and has_brand:
            filtered_contracts.append(contract)

    # Pagination in Python
    page = request.args.get('page', 1, type=int)
    per_page = 50
    total = len(filtered_contracts)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_contracts = filtered_contracts[start:end]

    class Pagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = end < total
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = Pagination(page, per_page, total)

    return render_template(
        "user_contract_info.html",
        contracts=paginated_contracts,
        pagination=pagination,
        user_categories=list(user_categories),
        user_brands=list(user_brands),
        assigned_start_date=assigned_start_date,
        assigned_end_date=assigned_end_date
    )




















@login_required
@user_bp.route("/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html", user=current_user)



@user_bp.route("/profile")
@login_required
def profile():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_profile.html", user=current_user)


@user_bp.route("/sellers")
@login_required
def sellers():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_seller_info.html", user=current_user)



@user_bp.route("/analytics")
@login_required
def analytics():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_analytics_info.html", user=current_user)


@user_bp.route("/contract")
@login_required
def contract():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_contract_info.html", user=current_user)