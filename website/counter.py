from flask import Blueprint, Response, request, redirect, url_for
from flask_login import current_user
import os
import time
import logging

counter = Blueprint('counter', __name__)

visitor_count_file = 'visitor_count.txt'
visitor_count = 0
your_ip = '73.44.112.191'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_visitor_count():
    try:
        if not os.path.exists(visitor_count_file):
            logging.info("Visitor count file does not exist, returning 0")
            return 0
        with open(visitor_count_file, 'r') as f:
            content = f.read().strip()
            count = int(content) if content else 0
            logging.info(f"Read visitor count: {count}")
            return count
    except Exception as e:
        logging.error(f"Error reading visitor count: {str(e)}")
        return 0

def save_visitor_count(count):
    try:
        with open(visitor_count_file, 'w') as f:
            f.write(str(count))
        logging.info(f"Saved visitor count: {count}")
    except Exception as e:
        logging.error(f"Error saving visitor count: {str(e)}")

visitor_count = get_visitor_count()

def event_stream():
    previous_count = -1
    while True:
        global visitor_count
        if visitor_count != previous_count:
            yield f"data: {visitor_count}\n\n"
            previous_count = visitor_count
        time.sleep(1)  # Prevent tight loop

@counter.before_request
def count_visits():
    global visitor_count
    if request.endpoint != 'counter.events' and request.remote_addr != your_ip:
        visitor_count += 1
        save_visitor_count(visitor_count)
        logging.info(f"Visitor count incremented to {visitor_count} for IP {request.remote_addr}")
    else:
        logging.info(f"Skipped visitor count for IP {request.remote_addr} or endpoint {request.endpoint}")

@counter.route('/events')
def events():
    return Response(event_stream(), mimetype='text/event-stream')

@counter.route('/visitor-counter')
def visitor_counter():
    if not current_user.is_authenticated or not current_user.is_admin:
        logging.warning(f"Unauthorized access to visitor counter by user {current_user.id if current_user.is_authenticated else 'anonymous'}")
        return redirect(url_for('views.home'))
    return render_template('visitor_counter.html', user=current_user)