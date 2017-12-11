from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

application = Flask(__name__)

AWS_ACCESS_KEY = 'j'
AWS_SECRET_KEY = 'k'
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


@application.route("/", methods=['GET', 'POST', 'PUT'])
def initial_page():
    print request.form
    if request.method == 'POST':
        if request.form['message'] == 'login':
            print request.form['message']
            print 'jjj'
            return redirect('login')
    return render_template('weshop.html')


@application.route("/login", methods=['GET', 'POST'])
def login():
    print request.form
    if request.method == 'POST':
        if not es.exists(index="users", doc_type="default", id=request.form['userId']):
            return jsonify({'status': 'failed', 'message': 'user does not exist'})
        else:
            user_info = es.get(index="users", doc_type="default", id=request.form['userId'])
            if user_info['_source']['password'] == request.form['info']['password']:
                return_json = user_info['_source']
                return_json.pop('password')
                return_json['status'] = 'success'

                return jsonify(return_json)
            else:
                return jsonify({'status': 'failed', 'message': 'incorrect password'})
    return render_template('login.html')


@application.route("/signup", methods=['GET', 'POST'])
def signup():
    print request.form
    if request.method == 'POST':
        if es.exists(index="users", doc_type="default", id=request.form['userId']):
            return jsonify({'status': 'failed', 'message': 'user already exists'})
        else:
            user_information = request.form['info']
            user_information['friends'] = []
            user_information['invited_events'] = []
            user_information['attending_events'] = []
            user_information['pending_friend_requests'] = []
            es.index(index="users", doc_type="default", id=request.form['userId'], body=user_information)
            return jsonify({'status': 'success', 'message': 'signup succeeded'})
    return render_template('signup.html')


if __name__ == '__main__':
    application.run()

