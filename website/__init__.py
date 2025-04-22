import os
from os import path
import logging
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate, init, migrate, upgrade
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
load_dotenv()

# Database configuration
DB_NAME = "database.db"
DB_PATH = path.join(path.abspath(path.dirname(__file__)), DB_NAME)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

def create_app() -> Flask:
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CSRFProtect(app)  # Initialize CSRF protection
    csrf.init_app(app)  # Ensure CSRF protection is applied
    
    # Register blueprints
    from .views import views
    from .auth import auth
    from .views import blog
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(blog)
    
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
    
    # Make current_user available in all templates
    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

   
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    return app

def create_database(app: Flask):
    try:
        with app.app_context():
            if not path.exists(DB_PATH):
                db.create_all()
                logging.info(f'Database created at {DB_PATH}')
    except Exception as e:
        logging.error(f'Error creating database: {e}')
        raise RuntimeError(f"Failed to create database: {e}")
    
