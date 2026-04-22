import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cloudinary

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # ─── BASIC CONFIG ─────────────────────────────
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY',
        'gracelawn-secret-key-2024-admin'
    )

    # ─── DATABASE (LOCAL + RAILWAY SUPPORT) ───────
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
    else:
        db_url = "sqlite:///" + os.path.join(app.root_path, "data.db")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ─── FILE UPLOAD (fallback only) ──────────────
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # ─── DEV SETTINGS ─────────────────────────────
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # ─── INIT EXTENSIONS ──────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'

    # ─── CLOUDINARY CONFIG (FIXED & SAFE) ─────────
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

    # ─── BLUEPRINTS ──────────────────────────────
    from app.blueprints.routes import main
    from app.blueprints.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    # ─── CREATE FOLDERS (LOCAL FALLBACK ONLY) ────
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'hero'), exist_ok=True)

    # ─── CONTEXT PROCESSOR ───────────────────────
    @app.context_processor
    def inject_unread():
        from flask_login import current_user
        from app.models import Message

        if current_user.is_authenticated:
            unread = Message.query.filter_by(read=False).count()
            return {'unread_count': unread}

        return {'unread_count': 0}

    # ─── CREATE TABLES ───────────────────────────
    with app.app_context():
        db.create_all()

    return app
app = create_app()