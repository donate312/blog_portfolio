import os
from os import path
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, session, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, current_user
from flask_migrate import Migrate, init, migrate, upgrade
from flask_wtf.csrf import CSRFProtect, generate_csrf
from datetime import timedelta

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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('/home/david/Desktop/portfolio/app.log')  # Log to file
    ]
)

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
      
    
    # Register blueprints
    from .views import views
    from .auth import auth
    from .views import blog
    from .counter import counter


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='')
    app.register_blueprint(blog, url_prefix='')
    app.register_blueprint(counter, url_prefix='/counter')
    
    # Import models and create database
    from .models import User, Note, Visitor
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

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)

    @app.before_request
    def track_visitor():
        excluded_ips = ['127.0.0.1', '73.44.112.191']
        visitor_ip = request.remote_addr

        if visitor_ip not in excluded_ips:
            existing_visitor = Visitor.query.filter_by(ip_address=visitor_ip).first()
            if not existing_visitor:
                new_visitor = Visitor(ip_address=visitor_ip)
                db.session.add(new_visitor)
                db.session.commit()
            logging.info(f'New visitor logged: {visitor_ip}')
        else:
            logging.info(f'Existing visitor: {visitor_ip}')
 
   # @app.context_processor
   # def inject_csrf_token():
    #    return dict(csrf_token=generate_csrf())
    
    @app.route("/refresh-csrf", methods=["GET"])
    def refresh_csrf():
        csrf_token = generate_csrf()
        return jsonify({'csrf_token': csrf_token}), 200
    
    file_handler = logging.FileHandler('/home/david/Desktop/portfolio/app.log')  # Use a writable directory
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    

    return app

def create_database(app: Flask):
        with app.app_context():
            if not path.exists(DB_PATH):
                db.create_all()
                logging.info(f'Database created at {DB_PATH}')
    