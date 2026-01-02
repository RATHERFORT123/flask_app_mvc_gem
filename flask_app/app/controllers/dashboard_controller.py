


from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from ..forms.auth import UserForm
from ..repositories import user_repository
from ..extensions import db
from ..models.contract import Contract
from ..models.seller import Seller
import json

dashboard_bp = Blueprint("dashboard", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@dashboard_bp.route("/dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html")


@dashboard_bp.route("/")
@login_required
def root():
    return redirect(url_for("dashboard.user_dashboard"))


@dashboard_bp.route("/dashboard2")
@login_required
@admin_required
def dashboard2():
    return render_template("admin_main_dashboard.html")


@dashboard_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    q = request.args.get("q", "").strip().lower()
    users = user_repository.get_all()
    if q:
        users = [u for u in users if q in u.username.lower() or q in u.email.lower()]
    return render_template("admin_dashboard.html", users=users, q=q)


@dashboard_bp.route("/admin/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def admin_user_create():
    form = UserForm()
    if form.validate_on_submit():
        user_repository.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data or "changeme123",
            is_admin=form.is_admin.data,
            is_verified=form.is_verified.data,
            is_blocked=form.is_blocked.data,
            address=form.address.data,
            number=form.number.data,
            comment=form.comment.data,
            category_names=form.category_names.data,
            brand_names=form.brand_names.data,
            assigned_date_range_start=form.assigned_date_range_start.data,
            assigned_date_range_end=form.assigned_date_range_end.data,
            subscription_date=form.subscription_date.data,
            amount=form.amount.data,
            payment_status=form.payment_status.data,
            subscription_plan=form.subscription_plan.data
        )
        flash("User created.", "success")
        return redirect(url_for("dashboard.admin_dashboard"))
    return render_template("admin_user_form.html", form=form, action="Create")



from flask import current_app

@dashboard_bp.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_user_edit(user_id):
    u = user_repository.get_by_id(user_id)
    if not u:
        abort(404)

    form = UserForm(obj=u)

    if request.method == "GET":
        form.category_names.data = u.category_names
        form.brand_names.data = u.brand_names
        form.assigned_date_range_start.data = u.assigned_date_range_start
        form.assigned_date_range_end.data = u.assigned_date_range_end
        form.subscription_date.data = u.subscription_date
        form.amount.data = u.amount
        form.payment_status.data = u.payment_status
        form.subscription_plan.data = u.subscription_plan

    if form.validate_on_submit():
        try:
            user_repository.update_user(
                u,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data or None,
                is_admin=form.is_admin.data,
                is_verified=form.is_verified.data,
                is_blocked=form.is_blocked.data,
                address=form.address.data,
                number=form.number.data,
                comment=form.comment.data,
                category_names=form.category_names.data,
                brand_names=form.brand_names.data,
                assigned_date_range_start=form.assigned_date_range_start.data,
                assigned_date_range_end=form.assigned_date_range_end.data,
                subscription_date=form.subscription_date.data,
                amount=form.amount.data,
                payment_status=form.payment_status.data,
                subscription_plan=form.subscription_plan.data
            )

            flash("User updated.", "success")
            return redirect(url_for("dashboard.admin_dashboard"))

        except Exception as e:
            # 🔥 CRITICAL
            db.session.rollback()

            current_app.logger.exception("User update failed")
            flash("Update failed. Please try again.", "danger")

    return render_template(
        "admin_user_form.html",
        form=form,
        action="Update"
    )


@dashboard_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_user_delete(user_id):
    u = user_repository.get_by_id(user_id)
    if not u:
        abort(404)
    if u.id == current_user.id:
        flash("You cannot delete your own admin account.", "warning")
        return redirect(url_for("dashboard.admin_dashboard"))
    user_repository.delete_user(u)
    flash("User deleted.", "success")
    return redirect(url_for("dashboard.admin_dashboard"))


@dashboard_bp.route("/admin/users/<int:user_id>/toggle-verify", methods=["POST"])
@login_required
@admin_required
def admin_user_toggle_verify(user_id):
    u = user_repository.get_by_id(user_id)
    if not u:
        abort(404)
    u.is_verified = not u.is_verified
    db.session.commit()
    flash("Verification status updated.", "success")
    return redirect(url_for("dashboard.admin_dashboard"))


@dashboard_bp.route("/admin/users/<int:user_id>/toggle-block", methods=["POST"])
@login_required
@admin_required
def admin_user_toggle_block(user_id):
    u = user_repository.get_by_id(user_id)
    if not u:
        abort(404)
    if u.id == current_user.id:
        flash("You cannot block/unblock your own admin account.", "warning")
        return redirect(url_for("dashboard.admin_dashboard"))
    u.is_blocked = not u.is_blocked
    db.session.commit()
    flash("User block status updated.", "success")
    return redirect(url_for("dashboard.admin_dashboard"))




@dashboard_bp.route("/admin/search/brands")
@login_required
@admin_required
def search_brands():
    term = request.args.get("term", "").lower()
    contracts = db.session.query(Contract.items).distinct().all()
    brands_set = set()
    for (items_json,) in contracts:
        if isinstance(items_json, list):
            for item in items_json:
                brand = item.get("brand")
                if brand and brand != "NaN":
                    brands_set.add(str(brand).strip())
    # Perform case-insensitive filtering
    if term:
        brands = [b for b in brands_set if term in b.lower()]
    else:
        brands = list(brands_set)
    return jsonify(sorted(brands))




@dashboard_bp.route("/admin/search/categories")
@login_required
@admin_required
def search_categories():
    term = request.args.get("term", "").strip().lower()
    categories_raw = db.session.query(Seller.category_name).distinct().all()
    all_categories = [c[0] for c in categories_raw if c[0]]
    if term:
        # Perform server-side filtering, case-insensitive
        categories = [cat for cat in all_categories if term in cat.lower()]
    else:
        categories = all_categories
    categories = sorted(categories)
    return jsonify(categories)



from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from ..forms.seller_form import SellerForm
from ..repositories import seller_repository
import re
import pandas as pd
from functools import wraps
from ..repositories import (
    user_repository,
    category_repository,
    contract_repository,
    brand_repository
)
from ..forms.auth import UserForm
from ..forms.category_form import CategoryForm
from ..forms.contract_form import ContractForm
from ..forms.brand_form import BrandForm
from ..extensions import db
import pandas as pd



@dashboard_bp.route("/admin/categories/upload_excel", methods=["GET", "POST"])
@login_required
@admin_required
def admin_category_upload_excel():
    form = UserForm()
    imported_categories = []
    if request.method == "POST":
        if 'excel_file' not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        file = request.files['excel_file']
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)
        if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            flash("Please upload an Excel file (.xls or .xlsx)", "danger")
            return redirect(request.url)
        try:
            df = pd.read_excel(file)
            required_columns = {'value', 'text'}
            if not required_columns.issubset(df.columns.str.lower()):
                flash(f"Excel must contain columns: {', '.join(required_columns)}", "danger")
                return redirect(request.url)
            df.columns = df.columns.str.lower()
            count = 0
            for _, row in df.iterrows():
                category_repository.add_category(row['value'], row['text'])
                count += 1
            flash(f"Successfully imported {count} categories.", "success")
            imported_categories = df.to_dict(orient='records')
        except Exception as e:
            flash(f"Failed to process Excel file: {str(e)}", "danger")
    return render_template("admin_user_upload_excel.html", form=form, action="Upload Categories", categories=imported_categories)

@dashboard_bp.route("/admin/categories/manage", methods=["GET", "POST"])
@login_required
@admin_required
def admin_category_manage():
    form = CategoryForm()
    categories = category_repository.get_all_categories()
    if form.validate_on_submit():
        if form.id.data:
            success = category_repository.update_category(form.id.data, form.value.data, form.text.data)
            if success:
                flash("Category updated.", "success")
            else:
                flash("Failed to update category.", "danger")
        else:
            if category_repository.add_category(form.value.data, form.text.data):
                flash("Category added.", "success")
            else:
                flash("Category with this value already exists.", "warning")
        return redirect(url_for("dashboard.admin_category_manage"))
    delete_id = request.args.get("delete_id")
    if delete_id:
        if category_repository.delete_category(delete_id):
            flash("Category deleted.", "success")
        else:
            flash("Category not found.", "warning")
        return redirect(url_for("dashboard.admin_category_manage"))
    edit_id = request.args.get("edit_id")
    if edit_id:
        category = next((c for c in categories if str(c.id) == edit_id), None)
        if category:
            form.id.data = category.id
            form.value.data = category.value
            form.text.data = category.text
    return render_template("admin_category_manage.html", form=form, categories=categories)

@dashboard_bp.route("/admin/contracts", methods=["GET", "POST"])
@login_required
@admin_required
def manage_contracts():
    form = ContractForm()
    page = request.args.get('page', 1, type=int)
    filters = {k: v for k, v in {
        'status': request.args.get('status', type=str),
        'organization_type': request.args.get('organization_type', type=str),
        'ministry': request.args.get('ministry', type=str),
        'department': request.args.get('department', type=str),
        'organization_name': request.args.get('organization_name', type=str),
        'office_zone': request.args.get('office_zone', type=str),
        'location': request.args.get('location', type=str),
        'buyer_designation': request.args.get('buyer_designation', type=str),
        'buying_mode': request.args.get('buying_mode', type=str),
        'bid_number': request.args.get('bid_number', type=str),
        'contract_date': request.args.get('contract_date', type=str),
        'total': request.args.get('total', type=float)
    }.items() if v is not None and v != ''}
    contracts_paginated = contract_repository.get_contracts_filtered_paginated(filters, page=page, per_page=50)
    contracts = contracts_paginated.items
    if form.validate_on_submit():
        data = form.data.copy()
        data.pop('csrf_token', None)
        items = [{
            'service': data.get('service'),
            'category_name': data.get('category_name'),
            'product': data.get('product'),
            'brand': data.get('brand'),
            'model': data.get('model'),
            'hsn_code': data.get('hsn_code'),
            'ordered_quantity': data.get('ordered_quantity'),
            'price': data.get('price')
        }]
        data['items'] = items
        if contract_repository.add_contract(data):
            flash('Contract added successfully.', 'success')
        else:
            flash('Failed to add contract.', 'danger')
        return redirect(url_for('dashboard.manage_contracts'))
    return render_template('admin_contracts.html', form=form, contracts=contracts, pagination=contracts_paginated, filters=filters)

@dashboard_bp.route("/admin/contracts/delete", methods=["POST"])
@login_required
@admin_required
def bulk_delete_contracts():
    contract_ids = request.form.getlist('contract_ids')
    contract_ids = list(map(int, contract_ids)) if contract_ids else []
    deleted_count = contract_repository.bulk_delete(contract_ids)
    flash(f"Deleted {deleted_count} contracts.", "success")
    return redirect(url_for('dashboard.manage_contracts'))

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

@dashboard_bp.route("/admin/contracts/upload_excel", methods=["GET", "POST"])
@login_required
@admin_required
def upload_contracts_excel():
    form = ContractForm()
    if request.method == 'POST':
        file = request.files.get('excel_file')

        # 🔵 ADD: file existence + extension check (already present, unchanged)
        if not file or not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            flash("Upload a valid Excel file (.xls or .xlsx)", "danger")
            return redirect(request.url)

        # 🔵 ADD: reset file pointer (CRITICAL for large files)
        file.stream.seek(0)

        # 🔵 ADD: safe Excel reading with explicit engine
        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            flash(f"Failed to read Excel file: {str(e)}", "danger")
            return redirect(request.url)

        # 🔵 ADD: empty Excel check
        if df.empty:
            flash("Uploaded Excel file is empty.", "danger")
            return redirect(request.url)

        # existing code (unchanged)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # 🔵 ADD: required column validation
        required_columns = {
            'contract_id', 'status', 'organization_type', 'ministry', 'department',
            'organization_name', 'office_zone', 'location', 'buyer_designation',
            'buying_mode', 'bid_number', 'contract_date', 'total',
            'service', 'category_name', 'product', 'brand', 'model',
            'hsn_code', 'ordered_quantity', 'price'
        }

        missing = required_columns - set(df.columns)
        if missing:
            flash(f"Missing required columns: {', '.join(missing)}", "danger")
            return redirect(request.url)

        # existing code (unchanged)
        contract_map = {}
        contract_fields = [
            'contract_id', 'status', 'organization_type', 'ministry', 'department',
            'organization_name', 'office_zone', 'location', 'buyer_designation',
            'buying_mode', 'bid_number', 'contract_date', 'total'
        ]

        item_fields = [
            'service', 'category_name', 'product', 'brand',
            'model', 'hsn_code', 'ordered_quantity', 'price'
        ]

        for _, row in df.iterrows():
            cid = row['contract_id']
            if cid not in contract_map:
                contract_map[cid] = {f: row.get(f) for f in contract_fields}
                contract_map[cid]['items'] = []

            item = {f: row.get(f) for f in item_fields}
            contract_map[cid]['items'].append(item)

        # existing code (unchanged)
        contracts = []
        for cid, contract_data in contract_map.items():
            contract_data['items'] = get_unique_items(contract_data['items'])
            contracts.append(contract_data)

        count = 0

        # 🔵 ADD: DB save protection
        for contract_data in contracts:
            try:
                if contract_repository.add_contract(contract_data):
                    count += 1
            except Exception as e:
                # skip failed contract but continue others
                continue

        flash(f"Successfully imported {count} contracts.", "success")
        return redirect(url_for('dashboard.manage_contracts'))

    return render_template("admin_contract_upload.html", form=form)



@dashboard_bp.route("/admin/brands/manage", methods=["GET", "POST"])
@login_required
@admin_required
def admin_brand_manage():
    form = BrandForm()
    brands = brand_repository.get_all_brands()
    if form.validate_on_submit():
        if form.id.data:
            success = brand_repository.update_brand(form.id.data, form.code.data, form.product_count.data, form.name.data)
            if success:
                flash("Brand updated.", "success")
            else:
                flash("Failed to update brand.", "danger")
        else:
            if brand_repository.add_brand(form.code.data, form.product_count.data, form.name.data):
                flash("Brand added.", "success")
            else:
                flash("Brand with this code already exists.", "warning")
        return redirect(url_for("dashboard.admin_brand_manage"))
    delete_id = request.args.get("delete_id")
    if delete_id:
        if brand_repository.delete_brand(delete_id):
            flash("Brand deleted.", "success")
        else:
            flash("Brand not found.", "warning")
        return redirect(url_for("dashboard.admin_brand_manage"))
    edit_id = request.args.get("edit_id")
    if edit_id:
        brand = next((b for b in brands if str(b.id) == edit_id), None)
        if brand:
            form.id.data = brand.id
            form.code.data = brand.code
            form.product_count.data = brand.product_count
            form.name.data = brand.name
    return render_template("admin_brand_manage.html", form=form, brands=brands)

@dashboard_bp.route("/admin/brands/upload_excel", methods=["GET", "POST"])
@login_required
@admin_required
def admin_brand_upload_excel():
    if request.method == "POST":
        file = request.files.get("excel_file")
        if not file or not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            flash("Please upload a valid Excel file (.xls or .xlsx)", "danger")
            return redirect(request.url)
        df = pd.read_excel(file)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        required_cols = {'code', 'product_count', 'brand'}
        if not required_cols.issubset(df.columns):
            flash("Excel file missing required columns: code, product_count, brand", "danger")
            return redirect(request.url)
        count = 0
        for _, row in df.iterrows():
            code_val = row['code'] if not pd.isna(row['code']) else 'Unknown'
            product_count_val = int(row['product_count']) if not pd.isna(row['product_count']) else 0
            brand_val = row['brand'] if not pd.isna(row['brand']) else 'Unknown'
            brand_repository.add_brand(code_val, product_count_val, brand_val)
            count += 1
        flash(f"Successfully imported {count} brands.", "success")
        return redirect(url_for("dashboard.admin_brand_manage"))
    return render_template("admin_brand_upload.html")

# -----------------------------seller----------------------------


@dashboard_bp.route('/admin/sellers/manage', methods=['GET', 'POST'])
@login_required
def manage_sellers():
    form = SellerForm()
    page = request.args.get('page', 1, type=int)
    filters = {k: v for k, v in {
        'contract_no': request.args.get('contract_no', type=str),
        'category_name': request.args.get('category_name', type=str),
        'seller_id': request.args.get('seller_id', type=str),
        'company_name': request.args.get('company_name', type=str),
        'contact_no': request.args.get('contact_no', type=str),
        'email': request.args.get('email', type=str),
        'msme_reg_no': request.args.get('msme_reg_no', type=str),
        'gstin': request.args.get('gstin', type=str),
        'generated_date': request.args.get('generated_date', type=str),
    }.items() if v}
    sellers_paginated = seller_repository.get_sellers_filtered_paginated(filters, page=page)
    sellers = sellers_paginated.items

    if form.validate_on_submit():
        data = form.data.copy()
        data.pop('csrf_token', None)
        if seller_repository.add_or_update_seller(data):
            flash("Seller added/updated successfully.", "success")
        else:
            flash("Failed to add/update seller.", "danger")
        return redirect(url_for('dashboard.manage_sellers'))

    delete_id = request.args.get('delete_id', type=int)
    if delete_id:
        deleted_count = seller_repository.bulk_delete_sellers([delete_id])
        if deleted_count > 0:
            flash("Seller deleted successfully.", "success")
        else:
            flash("Seller not found.", "warning")
        return redirect(url_for('dashboard.manage_sellers'))

    edit_id = request.args.get('edit_id', type=int)
    if edit_id:
        seller = next((s for s in sellers if s.id == edit_id), None)
        if seller:
            form.contract_no.data = seller.contract_no
            form.generated_date.data = seller.generated_date
            form.category_name.data = seller.category_name
            form.seller_id.data = seller.seller_id
            form.company_name.data = seller.company_name
            form.contact_no.data = seller.contact_no
            form.email.data = seller.email
            form.address.data = seller.address
            form.msme_reg_no.data = seller.msme_reg_no
            form.gstin.data = seller.gstin

    return render_template("admin_seller_manage.html", form=form, sellers=sellers, pagination=sellers_paginated, filters=filters)
@dashboard_bp.route('/admin/sellers/upload_excel', methods=['GET', 'POST'])
@login_required
def upload_sellers_excel():
    form = SellerForm()
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            flash("Upload a valid Excel file (.xls or .xlsx)", "danger")
            return redirect(request.url)

        def clean_column_name(c):
            c = c.strip().lower()
            c = c.replace(' ', '_')
            c = re.sub(r'[^\w]', '', c)  # remove dots and other punctuation
            return c

        df = pd.read_excel(file)
        df.columns = [clean_column_name(c) for c in df.columns]

        seller_fields = ['contract_no', 'generated_date', 'category_name', 'seller_id', 'company_name',
                         'contact_no', 'email', 'address', 'msme_reg_no', 'gstin']

        count = 0
        for _, row in df.iterrows():
            data = {field: row.get(field) for field in seller_fields}
            if seller_repository.add_or_update_seller(data):
                count += 1

        flash(f"Successfully imported {count} sellers.", "success")
        return redirect(url_for('dashboard.manage_sellers'))

    return render_template('admin_seller_upload.html', form=form)




from flask import (
    Blueprint,
    render_template,
    jsonify,
    abort
)
from flask_login import login_required, current_user
import threading
from flask import current_app

from ..services.contract_excel_worker import (
    process_next_pending,
    retry_all_failed,
    load_progress
)

# dashboard_bp = Blueprint("dashboard", __name__)

# -------------------------------------------------
# BACKGROUND THREAD RUNNER (WITH APP CONTEXT)
# -------------------------------------------------
_worker_thread = None


def run_bg(task_func):
    """
    Run background task with Flask app context.
    Prevent parallel execution.
    """
    global _worker_thread

    if _worker_thread and _worker_thread.is_alive():
        return False

    app = current_app._get_current_object()

    def wrapper():
        with app.app_context():
            task_func()

    _worker_thread = threading.Thread(target=wrapper)
    _worker_thread.daemon = True
    _worker_thread.start()

    return True


# =================================================
# ADMIN PAGE – EXCEL PROCESSOR UI
# =================================================
@dashboard_bp.route("/admin/contracts/excel-processor", methods=["GET"])
@login_required
def admin_contract_worker():
    if not current_user.is_admin:
        abort(403)

    return render_template("admin_contract_worker.html")


# =================================================
# PROCESS ONE PENDING EXCEL FILE
# =================================================
@dashboard_bp.route("/admin/contracts/process-pending", methods=["POST"])
@login_required
def process_pending():
    if not current_user.is_admin:
        abort(403)

    run_bg(process_next_pending)
    return jsonify({"status": "started"})


# =================================================
# RETRY ALL FAILED FILES
# =================================================
@dashboard_bp.route("/admin/contracts/retry-all", methods=["POST"])
@login_required
def retry_all():
    if not current_user.is_admin:
        abort(403)

    run_bg(retry_all_failed)
    return jsonify({"status": "retry_started"})


# =================================================
# LIVE PROGRESS API (POLLING)
# =================================================
@dashboard_bp.route("/admin/contracts/progress", methods=["GET"])
@login_required
def progress():
    if not current_user.is_admin:
        abort(403)

    return jsonify(load_progress())












from ..services.seller_excel_worker import (
    process_next_pending as process_seller_pending,
    retry_all_failed as retry_seller_failed,
    load_progress as seller_progress
)

# ---------------- SELLER UI ----------------

@dashboard_bp.route("/admin/sellers/excel-processor", methods=["GET"])
@login_required
def admin_seller_worker():
    if not current_user.is_admin:
        abort(403)
    return render_template("admin_seller_worker.html")


@dashboard_bp.route("/admin/sellers/process-pending", methods=["POST"])
@login_required
def process_seller_excel():
    if not current_user.is_admin:
        abort(403)

    run_bg(process_seller_pending)
    return jsonify({"status": "started"})


@dashboard_bp.route("/admin/sellers/retry-all", methods=["POST"])
@login_required
def retry_seller_excel():
    if not current_user.is_admin:
        abort(403)

    run_bg(retry_seller_failed)
    return jsonify({"status": "retry_started"})


@dashboard_bp.route("/admin/sellers/progress", methods=["GET"])
@login_required
def seller_progress_api():
    if not current_user.is_admin:
        abort(403)

    return jsonify(seller_progress())







from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
# from . import dashboard_bp
# from ..decorators import admin_required
from ..extensions import db
from ..models.brand import Brand
from ..models.contract import Contract
from ..forms.brand_form import BrandForm


# =====================================================
# Helper: extract EXACT brand names from contracts
# =====================================================

def extract_exact_brands_from_contracts():
    """
    Returns a set of brand names EXACTLY as stored in contracts
    (only trims leading/trailing spaces).
    """
    brands = set()

    contracts = Contract.query.with_entities(Contract.items).all()
    for (items,) in contracts:
        if not items:
            continue

        for item in items:
            if isinstance(item, dict):
                brand = item.get("brand")
                if isinstance(brand, str):
                    brand = brand.strip()
                    if brand:
                        brands.add(brand)

    return brands


# =====================================================
# Core logic: upload brands from contracts (exact)
# =====================================================

def upload_brands_from_contracts_exact():
    # Existing brand names (exact match)
    existing = {
        b.name for b in Brand.query.with_entities(Brand.name).all()
    }

    found = extract_exact_brands_from_contracts()

    inserted = 0
    for brand_name in found:
        if brand_name in existing:
            continue

        db.session.add(
            Brand(
                code=brand_name[:200],   # auto-generated code
                name=brand_name,         # EXACT SAME NAME
                product_count=0
            )
        )
        inserted += 1

    db.session.commit()
    return len(found), inserted


# =====================================================
# Brand Management Page
# =====================================================

@dashboard_bp.route("/admin/brands", methods=["GET", "POST"])
@login_required
@admin_required
def admin_brand_manage_page():

    form = BrandForm()
    edit_id = request.args.get("edit_id", type=int)
    delete_id = request.args.get("delete_id", type=int)

    # Delete brand
    if delete_id:
        brand = Brand.query.get_or_404(delete_id)
        db.session.delete(brand)
        db.session.commit()
        flash("Brand deleted successfully.", "success")
        return redirect(url_for("dashboard.admin_brand_manage_page"))

    # Edit brand
    editing_brand = None
    if edit_id:
        editing_brand = Brand.query.get_or_404(edit_id)
        form.code.data = editing_brand.code
        form.product_count.data = editing_brand.product_count
        form.name.data = editing_brand.name

    # Add / Update brand
    if form.validate_on_submit():
        if editing_brand:
            editing_brand.code = form.code.data
            editing_brand.product_count = form.product_count.data
            editing_brand.name = form.name.data
        else:
            db.session.add(
                Brand(
                    code=form.code.data,
                    product_count=form.product_count.data,
                    name=form.name.data
                )
            )
        db.session.commit()
        flash("Brand saved successfully.", "success")
        return redirect(url_for("dashboard.admin_brand_manage_page"))

    brands = Brand.query.order_by(Brand.name).all()
    return render_template(
        "admin_brand_manage.html",
        brands=brands,
        form=form,
        edit_brand=editing_brand
    )


# =====================================================
# Upload Brands from Contracts (ADMIN ACTION)
# =====================================================

@dashboard_bp.route("/admin/brands/upload-from-contracts", methods=["POST"])
@login_required
@admin_required
def admin_upload_brands_from_contracts_exact():

    total_found, inserted = upload_brands_from_contracts_exact()

    flash(
        f"Upload completed. Found {total_found} brands in contracts, "
        f"inserted {inserted} new brands.",
        "success"
    )
    return redirect(url_for("dashboard.admin_brand_manage_page"))
