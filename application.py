from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


application = Flask(__name__)
application.secret_key = 'super secret key'

AWS_ACCESS_KEY = '这里要改'
AWS_SECRET_KEY = '这里也要改'
region = 'us-east-1'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')

host = 'search-这里依然要改-tdsvvvhq4bobx7kcxq6jkaah6y.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

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
    if request.method =='POST':
        if not es.exists(index="users", doc_type="default", id=login_form['username']):
            return render_template('login.html', error = 'user does not exist')
        else:
            user_info = es.get(index="users", doc_type="default", id=login_form['username'])
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
        if es.exists(index="users", doc_type="default", id=signup_form['userId']):
            return render_template('signup.html', error = 'user already exists')
        else:
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
            user_information['pending_sent_requests'] = []
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
def viewfriendrequests():
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

        all_users = es.search(index='users', body={"query": {"match_all": {}}})['hits']['hits']
        # print all_users
        userId_list = []
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        curr_pending = es.get(index='users', doc_type='default', id=curr_user)['_source']['pending_sent_requests']
        for user in all_users:
            # print user['_id']
            if user['_id'] not in curr_friend_list and user['_id'] not in curr_pending and user['_id'] != curr_user:
                userId_list.append(
                    [user['_id'], user['_source']['firstname'], user['_source']['lastname'], user['_source']['phone']])
        # print "final user Id list", userId_list
        return render_template("AddFriends.html", **dict(data=userId_list))
    if request.method == 'POST':
        friendIds = request.form.getlist('FriendId')
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_user_info = es.get(index='users', doc_type='default', id=curr_user)['_source']
        for userId in friendIds:
            user_info = es.get(index='users', doc_type='default', id=userId)['_source']
            user_info['pending_friend_requests'].append(curr_user)
            curr_user_info['pending_sent_requests'].append(userId)
            es.index(index='users', doc_type='default', id=userId, body=user_info)
        print curr_user_info['pending_sent_requests']
        es.index(index='users', doc_type='default', id=curr_user, body=curr_user_info)
        print "hhah"
        return render_template('homepage.html')
    return render_template("AddFriends.html")

@application.route("/create_event", methods=['GET', 'POST'])
def create_event():
    event_form = request.form.to_dict()
    print event_form
    if request.method == 'GET':
        userId_list = []
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        for user in curr_friend_list:
            userId_list.append([user['_id'], user['_source']['firstname'], user['_source']['lastname']])
        print "ha"
        return render_template("create_event.html", **dict(friend=userId_list))
    if request.method == 'POST':
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        members = []
        members.append(event_form['memberlist'])
        members2 = []
        friend_members = []
        all_users = es.search(index='users', body={"query": {"match_all": {}}})['hits']['hits']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        event_information = {}
        event_information['event_name'] = event_form['eventName']
        if es.exists(index='events', doc_type='default', id=event_information['event_name']) 
            return render_template('create_event.html', error='event already exists')
        event_information['event_time'] = event_form['eventTime']
        event_information['member_list'] = members
        event_information['event_host'] = curr_user
        event_information['location'] = []
        if (members[-1] == "alluser"):
            for i in range(len(members) - 1):
                friend_members.append(members[i])
            members2.append(friend_members)
            for user in all_users:
                user = user['_id']
                if user not in curr_friend_list:
                    if user != curr_user:
                        members2.append([user])
                        event_information['pending_member_list'] = members2
        else :
            event_information['pending_member_list'] = members

        es.index(index="events", doc_type="default", id=event_form['eventName'], body=event_information)
        print es.get(index='events', doc_type='default', id=event_form['eventName'])
        return redirect('/homepage')
    return render_template('create_event.html')

if __name__ == '__main__':
    application.run()


