from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from flask_paginate import Pagination, get_page_args


application = Flask(__name__)
application.secret_key = 'super secret key'

AWS_ACCESS_KEY = 'i'
AWS_SECRET_KEY = 'j'
region = 'us-east-1'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')

host = 'search-test-tdsvvvhq4bobx7kcxq6jkaah6y.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

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
            return redirect('login')
    return render_template('weshop.html')


@application.route("/login", methods=['GET', 'POST'])
def login():
    # print request.form
    login_form = request.form.to_dict()
    print login_form
    if request.method =='POST':
        print "here!"
        if not es.exists(index="users", doc_type="default", id=login_form['username']):
            print 1
            return render_template('login.html', error = 'user does not exist')
        else:
            print 2
            user_info = es.get(index="users", doc_type="default", id=login_form['username'])
            print user_info['_source']['password']
            print login_form['password']
            if user_info['_source']['password'] == login_form['password']:
                return_json = user_info['_source']
                return_json.pop('password')
                return_json['status'] = 'success'
                session['curr_userid'] = login_form['username']
                return render_template('homepage.html')
            else:
                return render_template('login.html', error = 'incorrect password')
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
            session['curr_userid'] = signup_form['userId']
            return redirect('/homepage')
    return render_template('signup.html')

@application.route("/homepage", methods=['GET', 'POST'])
def homepage():
    signup_form = request.form.to_dict()
    if request.method == 'GET':
       if 'curr_userid' in session:
         userid = session['curr_userid']
       return render_template('homepage.html')

@application.route("/viewfriendrequests", methods=['GET', 'POST'])
def add_friend():
    if request.method == 'GET':
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
        pending_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['pending_friend_requests']
        for user in all_users:
            if user not in pending_friend_list:
                userId_list.append([user['_id'], user['_source']['firstname'], user['_source']['lastname'], user['_source']['phone']])
        return render_template("ViewPendingFriendRequest.html", **dict(data=userId_list))
    if request.method == 'POST':
        friendIds = request.form.getlist('FriendId')
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
        for userId in friendIds:
            user_info = es.get(index='users', doc_type='default', id=userId)['_source']
            user_info['friends'].append(curr_user)
            es.index(index='users', doc_type='default', id=userId, body=user_info)
        user_info = es.get(index='users', doc_type='default', id=curr_user)['_source']
        print(user_info)
        return render_template('homepage.html')

@application.route("/viewfriends", methods=['GET', 'POST'])
def viewfriends():
    if request.method == 'GET':
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
          friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        for user in friend_list:
             userId_list.append([user['_id'], user['_source']['firstname'], user['_source']['lastname'], user['_source']['phone']])
        return render_template("FriendList.html", **dict(data=friend_list))
   
@application.route("/addfriends", methods=['GET', 'POST'])
def add_friend():
    if request.method == 'GET':
        all_users = es.search(index='users', body={"query":{"match_all":{}}})['hits']['hits']
        userId_list = []
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        for user in all_users:
            if user not in curr_friend_list:
                userId_list.append([user['_id'], user['_source']['firstname'], user['_source']['lastname'], user['_source']['phone']])
            return render_template("AddFriends.html", **dict(data=userId_list))
    if request.method == 'POST':
        friendIds = request.form.getlist('FriendId')
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
        for userId in friendIds:
            user_info = es.get(index='users', doc_type='default', id=userId)['_source']
            user_info['pending_friend_requests'].append(curr_user)
            es.index(index='users', doc_type='default', id=userId, body=user_info)
        user_info = es.get(index='users', doc_type='default', id=curr_user)['_source']
        print(user_info)
        return render_template('homepage.html')
    return render_template("AddFriends.html")



# @application.route("/createevents", methods=['GET', 'POST'])


if __name__ == '__main__':
    application.run()
    # print es.search(index='users', body={"query": {"match_all": {}}})['hits']['hits']

