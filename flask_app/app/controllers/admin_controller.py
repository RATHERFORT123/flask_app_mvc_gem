from urllib import request
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from ..models.contract import Contract
from ..models.seller import Seller
from ..models.ucfd import UCFD
from ..extensions import db
from functools import wraps
from flask import request

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def extract_unique_contract_fields():
    fields = [
        'status','organization_type','ministry','department','organization_name','office_zone',
        'location','buyer_designation','buying_mode','bid_number','contract_date','total'
    ]
    unique_values = set()
    contracts = Contract.query.all()
    for contract in contracts:
        row = tuple(getattr(contract, f) for f in fields)
        unique_values.add(row)
    return [dict(zip(fields, row)) for row in unique_values]

def extract_unique_items_fields():
    item_fields = ['service','product','brand','model','hsn_code','ordered_quantity','price']
    unique_items = set()
    contracts = Contract.query.all()
    for contract in contracts:
        if contract.items:
            for item in contract.items:
                row = tuple(item.get(f) for f in item_fields)
                unique_items.add(row)
    return [dict(zip(item_fields, row)) for row in unique_items]

def extract_unique_seller_fields():
    seller_fields = [
        'generated_date','category_name','seller_id','company_name','contact_no',
        'email','address','msme_reg_no','gstin'
    ]
    unique_sellers = set()
    sellers = Seller.query.all()
    for seller in sellers:
        row = tuple(getattr(seller, f) for f in seller_fields)
        unique_sellers.add(row)
    return [dict(zip(seller_fields, row)) for row in unique_sellers]





# @admin_bp.route("/ucfd_view", methods=["GET", "POST"])
# @login_required
# @admin_required
# def ucfd_view():
#     if not current_user.is_admin:
#         return "403 Forbidden", 403

#     if 'fetch' in (getattr(current_user, 'request', None) or {}):
#         # On button click
#         contract_uniques = extract_unique_contract_fields()
#         items_uniques = extract_unique_items_fields()
#         seller_uniques = extract_unique_seller_fields()
#         all_rows = contract_uniques + items_uniques + seller_uniques
#         for data in all_rows:
#             try:
#                 ucfd_row = UCFD(**data)
#                 db.session.add(ucfd_row)
#                 db.session.commit()
#             except IntegrityError:
#                 db.session.rollback()
                
#     page = int(request.args.get("page", 1))
#     per_page = 50
#     # ucfd_rows = UCFD.query.paginate(page, per_page, False)
#     ucfd_rows = UCFD.query.paginate(page=page, per_page=per_page, error_out=False)

#     return render_template("admin_ucfd_filter.html", ucfd=ucfd_rows.items, pagination=ucfd_rows)



@admin_bp.route("/ucfd_view", methods=["GET"])
@login_required
@admin_required
def ucfd_view():
    if request.args.get('fetch'):
        contract_uniques = extract_unique_contract_fields()
        items_uniques = extract_unique_items_fields()
        seller_uniques = extract_unique_seller_fields()
        all_rows = contract_uniques + items_uniques + seller_uniques
        for data in all_rows:
            try:
                ucfd_row = UCFD(**data)
                db.session.add(ucfd_row)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    page = int(request.args.get("page", 1))
    per_page = 50
    ucfd_rows = UCFD.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("admin_ucfd_filter.html", ucfd=ucfd_rows.items, pagination=ucfd_rows)
