from flask import Flask, request, render_template, jsonify
from subprocess import *
import random
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

application = Flask(__name__)

AWS_ACCESS_KEY = 'AKIAJD4VHHXO4KJBT64Q'
AWS_SECRET_KEY = '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'
region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = 'search-test-qaqcu3tpmtqedbutv744acsjm4.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com


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

    return render_template('main_page.html')

if __name__ == '__main__':
    application.run()