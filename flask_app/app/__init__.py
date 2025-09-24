from flask import Flask, render_template
from .extensions import db, migrate, login_manager, csrf
from .controllers.auth_controller import auth_bp
from .controllers.dashboard_controller import dashboard_bp
from .controllers.user_controller import user_bp  # if implemented user_controller

from .models.user import User

def create_app(config_object="config.DevConfig"):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)  # Uncomment if you implement user_controller

    register_errorhandlers(app)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username="admin",
                email="admin@example.com",
                is_admin=True,
                is_verified=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    return app

def register_errorhandlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500




# from flask import Flask
# from .extensions import db, migrate, login_manager, csrf
# from .models.user import User
# from .controllers.auth_controller import auth_bp
# from .controllers.dashboard_controller import dashboard_bp
# # from . import brand_repository

# def create_app(config_object="config.DevConfig"):
# #  if not User.query.filter_by(is_admin=True).first():

#     app = Flask(__name__, static_folder="static", template_folder="templates")
#     app.config.from_object(config_object)

#     # Init extensions
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login_manager.init_app(app)
#     csrf.init_app(app)

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     # Blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(dashboard_bp)

#     # Create tables (only for SQLite/dev convenience)
#     with app.app_context():
#         db.create_all()

#         # Ensure there's an initial admin if none exists
#         if not User.query.filter_by(is_admin=True).first():
#             admin = User(
#                 username="admin",
#                 email="admin@example.com",
#                 is_admin=True,
#                 is_verified=True,
#             )
#             admin.set_password("admin123")  # Change in production!
#             db.session.add(admin)
#             db.session.commit()

#     return app



