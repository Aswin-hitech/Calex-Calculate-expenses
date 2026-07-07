from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
import os

# Extensions instantiated here for import elsewhere

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

mail = Mail()

jwt = JWTManager()

def create_app():
    """Application factory pattern.

    Returns:
        Flask: Configured Flask application instance.
    """
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, instance_relative_config=False, template_folder=template_dir, static_folder=static_dir)
    # Load configuration from config.py or environment
    app.config.from_object('config.Config')
    app.url_map.strict_slashes = False

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def too_large(_error):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def server_error(_error):
        return render_template('errors/500.html'), 500

    # Register blueprints
    from flask_login import current_user

    from .auth.routes import auth_bp
    from .expenses.routes import expenses_bp
    from .income.routes import income_bp
    from .budgets.routes import budgets_bp
    from .analytics.routes import analytics_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(income_bp, url_prefix='/income')
    app.register_blueprint(budgets_bp, url_prefix='/budgets')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Home route – dashboard if logged in, else landing page
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('dashboard.html')
        return render_template('landing.html')

    @app.route('/healthz')
    def healthcheck():
        return jsonify(status='ok')

    return app
