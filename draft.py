from flask import Flask, request, render_template, jsonify
from subprocess import *
import random

application = Flask(__name__)

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
region = 'us-east-1'
service = 'es'



@application.route("/", methods=['GET', 'POST'])
def main_page():
    if request.form['type'] == 'login':
        pass
    elif request.form['type'] == 'signup':
        pass
    elif request.form['type'] == 'create_event':
        pass
    elif request.form['type'] == '':
        pass
