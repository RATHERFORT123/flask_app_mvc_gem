from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from ..forms.auth import SignupForm, LoginForm
from ..services.auth_service import authenticate, register

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.user_dashboard"))
    form = SignupForm()
    if form.validate_on_submit():
        register(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            address=form.address.data,
            number=form.number.data,
        )
        flash("Account created. Please wait for admin verification.", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard.user_dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next") or url_for(
                "dashboard.admin_dashboard" if user.is_admin else "dashboard.user_dashboard"
            )
            return redirect(next_url)
        else:
            flash("Invalid credentials or blocked account.", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

