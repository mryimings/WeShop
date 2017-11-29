from flask import Flask, request, render_template, jsonify
from subprocess import *
import random
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

application = Flask(__name__)

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
region = 'us-east-1'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')

host = 'search-test-qaqcu3tpmtqedbutv744acsjm4.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


@application.route("/", methods=['GET', 'POST'])
def main_page():
    if request.form['type'] == 'login':
        pass

    elif request.form['type'] == 'signup':
        if es.exists(index="", doc_type="", id=request.form['userId']):
            return jsonify({'status': 'failed', 'message': 'user already exists'})
        else:
            es.index(index="", doc_type="", id=request.form['userId'], body=request.form['info'])
            return jsonify({'status': 'success', 'message': 'signup succeeded'})

    elif request.form['type'] == 'create_event':
        pass
    elif request.form['type'] == '':
        pass

    return render_template('main_page.html')

if __name__ == '__main__':
    application.run()
