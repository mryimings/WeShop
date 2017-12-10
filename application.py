from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

application = Flask(__name__)

# AWS_ACCESS_KEY = 'j'
# AWS_SECRET_KEY = 'k'
# region = 'us-east-1'
#
# awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')
#
# host = 'search-test-qaqcu3tpmtqedbutv744acsjm4.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com
#
# es = Elasticsearch(
#     hosts=[{'host': host, 'port': 443}],
#     http_auth=awsauth,
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection
# )


@application.route("/", methods=['GET', 'POST', 'PUT'])
def initial_page():
    print request


    if request.method == 'POST':
        if request.form['message'] == 'login':
            print request.form['message']
            print 'jjj'
            return redirect('login')
    return render_template('weshop.html')


@application.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@application.route("/signup", methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    application.run()


