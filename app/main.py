#!/usr/bin/env python

import logging
import os

# import RPi.GPIO as GPIO

import flask
from flask.app import Flask
import flask_wtf
from flask import render_template, request, session, url_for, redirect, Response
from camera import VideoCamera
#from flask_mysqldb import MySQL
#import MySQLdb
import mysql.connector
from werkzeug import exceptions
import threading
import time

import api
import json_response
import socket_api
import views
import datetime
from find_files import find as find_files


#For servomotor
from gpiozero import Servo
import RPi.GPIO as GPIO
from time import sleep


database = mysql.connector.connect(user='root',password='26799',
                           host='127.0.0.1',
                           database='login')
cursor = database.cursor()

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

#Define the pins that you want
servopin = 26
servopin2=16

#Motor status


GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)

#Defining pins
GPIO.setup(servopin,GPIO.OUT)
GPIO.setup(servopin2,GPIO.OUT)

usb =GPIO.PWM(servopin,50)
usb.start(0)
sorc =GPIO.PWM(servopin2,50)
sorc.start(0)


# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)

app.register_blueprint(api.api_blueprint)
app.register_blueprint(views.views_blueprint)


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

@app.route('/home')
def home():
    return render_template('index.html',custom_elements_files=find_files.custom_elements_files())


@app.route('/connections')
def connect():
    return render_template('connections.html',find_files.all_frontend_files())  

  
@app.route("/<device>/<action>")
def action(device, action):
       #p.start(0)
       if device ==  'source':
           p = sorc
       if device == 'usb':
           p = usb
       if action == 'on':
                 p.ChangeDutyCycle(1.5)
                  #servo.value = 0
                 sleep(1)
                 #servo.value = None
                 #sleep(5)
       if action == 'off':
           #servo.value = 1
           p.ChangeDutyCycle(5)
           sleep(1)
           #p.ChangeDutyCycle()
           #servo.value = None
           #sleep(5)
       p.ChangeDutyCycle(40)
       return render_template('connections.html',find_files.all_frontend_files())


@app.route('/',methods=['GET','POST'])
def login():

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        #logger.info(username,password) 
        #cursor = database.connection.cursor(.cursors.DictCursor)
        cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s",(username,password))
        # Check if account exists using MySQL
        #cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM from login_info WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        info = cursor.fetchone()
        #print(info[0], info[1], info[2]) 
        # If account exists in accounts table in out database
        if info:
            if info[0] == username :
                if info[1] == password:
                    msg =  "login succesfull"
                    return render_template(
                        'index.html',
                        custom_elements_files=find_files.custom_elements_files(),msg=msg)

                else:
                    msg = "Incorrect password "
                    return render_template(
                        'index.html',
                        custom_elements_files=find_files.custom_elements_files(),msg=msg)
            else:
                # Account doesnt exist or username/password incorrect
                #return "login unsuc"
                msg = 'Incorrect username/password!'
                return render_template(
                    'login.html',
                    ustom_elements_files=find_files.custom_elements_files(),msg=msg)
        else:
            msg = "The user doesnt have permission"
        #return redirect(url_for('home'))
    return render_template(
         'login.html',
         custom_elements_files=find_files.custom_elements_files(),msg = msg)

  
def main(): 
    #database.run(debug=True)
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

