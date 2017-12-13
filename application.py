from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

application = Flask(__name__)

AWS_ACCESS_KEY = 'AKIAIMTPCPWPEM5XYLKQ'
AWS_SECRET_KEY = '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'
region = 'us-east-1'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')

host = 'search-weshop-zfky4prhxjrqo6xjo74ql4eheq.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

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
    # print request.form
    signup_form = request.form.to_dict()
    print signup_form
    if request.method =='POST':
        print "here!"
        if not es.exists(index="users", doc_type="default", id=signup_form['username']):
            print 1
            return jsonify({'status': 'failed', 'message': 'user does not exist'})
        else:
            print 2
            user_info = es.get(index="users", doc_type="default", id=signup_form['username'])
            print user_info['_source']['password']
            print signup_form['password']
            if user_info['_source']['password'] == signup_form['password']:
                return_json = user_info['_source']
                return_json.pop('password')
                return_json['status'] = 'success'

                return jsonify(return_json)
            else:
                return jsonify({'status': 'failed', 'message': 'incorrect password'})
    return render_template('login.html')


@application.route("/signup", methods=['GET', 'POST'])
def signup():
    signup_form = request.form.to_dict()
    if request.method == 'POST':
        print "here!"
        if es.exists(index="users", doc_type="default", id=signup_form['userId']):
            return render_template('signup.html', error = 'user already exists')
        else:
            print 2
            user_information = {}
            user_information['userId'] = signup_form['userId']
            user_information['password'] = signup_form['password']
            user_information['firstname'] = signup_form['firstname']
            user_information['lastname'] = signup_form['lastname']
            user_information['phone'] = signup_form['phone']
            user_information['address'] = signup_form['building']
            user_information['friends'] = []
            user_information['invited_events'] = []
            user_information['attending_events'] = []
            user_information['pending_friend_requests'] = []
            es.index(index="users", doc_type="default", id=signup_form['userId'], body=user_information)
            print es.get(index='users', doc_type='default', id=signup_form['userId'])
            return render_template('weshop.html')
    return render_template('signup.html')


if __name__ == '__main__':
     application.run()
