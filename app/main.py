#!/usr/bin/env python

import logging
import os

# import RPi.GPIO as GPIO

import flask
import flask_wtf
from flask import render_template, request
from werkzeug import exceptions

import api
import json_response
import socket_api
import views
from find_files import find as find_files

host = os.environ.get('HOST', '127.0.0.1')
port = int(os.environ.get('PORT', 8000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '0') == '1'

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    # Socket.io logs are too chatty at INFO level.
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.info('Starting app')

app = flask.Flask(__name__, static_url_path='')
app.config.update(
    SECRET_KEY=os.urandom(32),
    TEMPLATES_AUTO_RELOAD=True,
    WTF_CSRF_TIME_LIMIT=None,
)
app.config.from_envvar('APP_SETTINGS_FILE')

#Configure GPIO

#Define the pins that you want
motor = 20
#Motor status
motorsts = 0

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# buttonSts = GPIO.LOW

# GPIO.setup(motor, GPIO.OUT)

# GPIO.output(motor,GPIO.LOW)



# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)

app.register_blueprint(api.api_blueprint)
app.register_blueprint(views.views_blueprint)


# @app.route("/<deviceName>/<action>")
# def action(deviceName, action):
#     if deviceName == 'motor':
#         GPIO.output(motor,GPIO.HIGH)

#     template_data = {
#         'motor' : motorsts
#         }
#     motorsts = GPIO.input(motor)
#     return render_template('index.html', **template_data)


@app.errorhandler(flask_wtf.csrf.CSRFError)
def handle_csrf_error(error):
    return json_response.error(error), 403


@app.after_request
def after_request(response):
    # Disable caching in debug mode.
    if debug:
        response.headers['Cache-Control'] = (
            'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0')
        response.headers['Expires'] = 0
        response.headers['Pragma'] = 'no-cache'
    return response


@app.errorhandler(Exception)
def handle_error(e):
    logger.exception(e)
    code = 500
    if isinstance(e, exceptions.HTTPException):
        code = e.code
    return json_response.error(e), code


# @app.route('/')
# def home():
#    templateData = {
#       'motor' : 0,
      
#    }
#    return render_template('index.html', **templateData)

# @app.route('/<led>/<action>')
# def led(led, action):
#    #GPIO.output(int(led), int(action))
#    templateData = {
#       #'motor' : GPIO.input(motor)
#       'motor' : 1
#    }
#    return render_template('index.html', **templateData)

#pin_state  =  socket_api.socket_send()

#logger.info(pin_state)



def main(): 
    
    socketio = socket_api.socketio
    socketio.init_app(app)
    socketio.run(app,
                 host=host,
                 port=port,
                 debug=debug,
                 use_reloader=use_reloader,
                 extra_files=find_files.all_frontend_files())


if __name__ == '__main__':
    main()

