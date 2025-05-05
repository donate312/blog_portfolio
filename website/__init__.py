import os
from os import path
import logging
from dotenv import load_dotenv
from flask_mail import Mail
from flask import Flask, render_template, session, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate, init, migrate, upgrade
from flask_wtf.csrf import CSRFProtect, generate_csrf
from datetime import timedelta
from uuid import uuid4

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
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
    app = Flask(__name__) # Initialize Flask app
    #csrf.init_app(app)  # Initialize CSRF protection
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
     # Flask-Mail configuration for Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'david.onate312@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # Replace with Gmail App Password
    app.config['MAIL_DEFAULT_SENDER'] = 'david.onate312@gmail.com'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init.app(app)
    mail.init_app(app)
         
    # Register blueprints
    from .views import views
    from .auth import auth
    from .blog import blog
    from .counter import counter


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(blog, url_prefix='/')
    app.register_blueprint(counter, url_prefix='/counter')
    
    # Import models and create database
    from .models import User, Note, Visitor, ContactMessage, BlogPost
    
    with app.app_context():
        db.create_all()  # Create database tables
        #create_database(app)
    
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
                new_visitor = Visitor(
                    ip_address=visitor_ip,
                    session_id=str(uuid4()),
                    is_guest=current_user.is_guest if current_user.is_authenticated else False
                )
                db.session.add(new_visitor)
                db.session.commit()
            logging.info(f'New visitor logged: {visitor_ip}')
        else:
            logging.info(f'Existing visitor: {visitor_ip}')
 
    @app.before_request
    def require_login():
        # list of endpoints that don't require login
        exempt_routes = [
            'auth.login',           
            'auth.guest_login',
            'auth.logout',
            'static',  # Allow access to static files (e.g., CSS, JS, images)
            'refresh-csrf'  # Allow CSRF token refresh
        ]
        if request.endpoint not in exempt_routes and not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
    
    @app.route("/refresh-csrf", methods=["GET"])
    def refresh_csrf():
        csrf_token = generate_csrf()
        return jsonify({'csrf_token': csrf_token}), 200
    
    file_handler = logging.FileHandler('/home/david/Desktop/portfolio/app.log')  # Use a writable directory
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    

    return app

#def create_database(app: Flask):
 #       with app.app_context():
  #          if not path.exists(DB_PATH):
   #             db.create_all()
    #            logging.info(f'Database created at {DB_PATH}')
    