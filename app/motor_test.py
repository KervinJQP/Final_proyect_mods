
import os
import RPi.GPIO as GPIO
from gpiozero import Servo
from flask import Flask, render_template, request
from time import sleep
app = Flask(__name__)
#GPIO.cleanup()
servopin=26
servopin2=16
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(servopin,GPIO.OUT)
GPIO.setup(servopin2,GPIO.OUT)

usb =GPIO.PWM(servopin,50)
usb.start(0)
sorc =GPIO.PWM(servopin2,50)
sorc.start(0)

#servo =Servo(servopin)


@app.route("/")
def index():

            #usb.stop()
            #sorc.stop()
            #GPIO.cleanup()
            return render_template('main.html')

@app.route("/connections")
def connect():
            #usb.start(0)
            #sorc.start(0)
            return render_template('index.html')

@app.route("/<device>/<action>")
def action(device, action):
       #p.start(0)
       if device ==  'source':
           p = sorc
       if device == 'usb':
           p = usb
