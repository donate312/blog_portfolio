import os
from os import path
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Database configuration
DB_NAME = "database.db"
DB_PATH = path.abspath(path.join(path.dirname(__file__), DB_NAME))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_app() -> Flask:
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    if not os.getenv('SECRET_KEY'):
        logging.warning("SECRET_KEY is not set in the environment. Using default_secret_key.")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Import models and create database
    from .models import User, Note
    create_database(app)
    
    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id: str):
        return User.query.get(int(id))
    
    # make current_user available in all templates
    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    return app

def create_database(app: Flask):
    with app.app_context():
        db_path = path.join('website', DB_NAME)
        if not path.exists(db_path):
            try:
                from flask_migrate import upgrade
                upgrade()  # Apply migrations
                logging.info(f'Database created and migrations applied at {db_path}')
            except Exception as e:
                logging.error(f'Error applying migrations: {e}')
                raise RuntimeError(f"Failed to apply migrations: {e}")