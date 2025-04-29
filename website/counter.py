from flask import Blueprint, Response, request
import os
import time

counter = Blueprint('counter', __name__)

visitor_count_file = 'visitor_count.txt'
visitor_count = 0
your_ip = '73.44.112.191'

def get_visitor_count():
    if not os.path.exists(visitor_count_file):
        return 0
    with open(visitor_count_file, 'r') as f:
        return int(f.read())
      
def save_visitor_count(count):
    with open(visitor_count_file, 'w') as f:
        f.write(str(count))

visitor_count = get_visitor_count()

#stream visiotr count updates
def event_stream():
    previous_count = -1
    while True:
        global visitor_count
        if visitor_count != previous_count:
            yield f"data: {visitor_count}\n\n"
        previous_count = visitor_count

@counter.before_request
def count_visits():
    global visitor_count
    if request.endpoint != 'counter.events' and request.remote_addr != your_ip:    
        visitor_count += 1
        save_visitor_count(visitor_count)

@counter.route('/events')
def events():
    return Response(event_stream(), mimetype='text/event-stream')