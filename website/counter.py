from flask import Blueprint, Response, request, redirect, url_for
from flask_login import current_user
from . import db
from .models import Visitor
import time
import logging
from uuid import uuid4

counter = Blueprint('counter', __name__)

your_ip = '73.44.112.191'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/david/Desktop/portfolio/app.log')
    ]
)

def get_visitor_count():
    try:
        count = Visitor.query.count()
        logging.info(f"Visitor count from database: {count}")
        return count
    except Exception as e:
        logging.error(f"Error querying visitor count: {str(e)}")
        return 0

@counter.before_request
def count_visits():
    if request.endpoint != 'counter.events' and request.remote_addr != your_ip:
        visitor_ip = request.remote_addr
        try:
            # Check if IP already exists
            existing_visitor = Visitor.query.filter_by(ip_address=visitor_ip).first()
            if not existing_visitor:
                new_visitor = Visitor(
                    ip_address=visitor_ip,
                    session_id=str(uuid4()),
                    is_guest=current_user.is_guest if current_user.is_authenticated else False
                )
                db.session.add(new_visitor)
                db.session.commit()
                logging.info(f"New visitor added: IP={visitor_ip}, Count={get_visitor_count()}")
            else:
                logging.info(f"Existing visitor: IP={visitor_ip}, Count={get_visitor_count()}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding visitor: {str(e)}")
    else:
        logging.info(f"Skipped visitor count for IP={request.remote_addr}, Endpoint={request.endpoint}")

def event_stream():
    previous_count = -1
    while True:
        current_count = get_visitor_count()
        if current_count != previous_count:
            yield f"data: {current_count}\n\n"
            previous_count = current_count
        time.sleep(1)  # Prevent tight loop

@counter.route('/events')
def events():
    return Response(event_stream(), mimetype='text/event-stream')

@counter.route('/visitor-counter')
def visitor_counter():
    if not current_user.is_authenticated or not current_user.is_admin:
        logging.warning(f"Unauthorized access to visitor counter by user {current_user.id if current_user.is_authenticated else 'anonymous'}")
        return redirect(url_for('views.home'))
    return render_template('visitor_counter.html', user=current_user, visitor_count=get_visitor_count())