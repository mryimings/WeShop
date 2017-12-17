from flask import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from subprocess import *

application = Flask(__name__)
application.secret_key = 'super secret key'

AWS_ACCESS_KEY = 'i'
AWS_SECRET_KEY = 'j'
region = 'us-east-1'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, 'es')

host = 'search-test-tdsvvvhq4bobx7kcxq6jkaah6y.us-east-1.es.amazonaws.com'  #


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
            user_information['address'] = signup_form['building'] + "," + signup_form['street'] + "," + signup_form['city'] + "," + signup_form['state'] + "," + signup_form['zipcode']
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

@application.route('/main_event_status', methods=['GET', 'POST'])
def main_event_status():
    main_event_status_form = request.form.to_dict()
    print main_event_status_form
    if request.method == 'GET':
        curr_user = ''
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        all_events = es.search(index='events', body={"query":{"match_all":{}}})['hits']['hits']
        host_events = []
        pending_events = []
        accepted_events = []
        print all_events
        for event in all_events:
            print event['_id']
            if curr_user == event['_source']['event_host']:
                host_events.append(event['_id'])
            elif curr_user in event['_source']['pending_member_list']:
                pending_events.append([event['_id'], event['_source']['location'], event['_source']['event_time']])
            elif curr_user in event['_source']['accepted_member_list']:
                accepted_events.append([event['_id'], event['_source']['location'], event['_source']['event_time']])
        print host_events
        print pending_events
        print accepted_events
        return render_template('main_event_status.html', **dict(host=host_events, pending=pending_events, accepted=accepted_events))
    elif request.method == 'POST':
        decision_dict = request.form.to_dict()
        # print "decision:", decision_dict
        curr_user = ''
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_user_info = es.get(index='users', doc_type='default', id=curr_user)['_source']
        for event_id in decision_dict:
            if event_id != 'eventDecision':
                # print event_id, curr_user
                # print curr_user_info['invited_events']

                curr_user_info['invited_events'].remove(event_id)
                curr_event_info = es.get(index='events', doc_type='default', id=event_id)['_source']
                # print curr_event_info['pending_member_list']
                curr_event_info['pending_member_list'].remove(curr_user)
                if decision_dict[event_id] == 'yes':
                    curr_user_info['attending_events'].append(event_id)
                    curr_event_info['accepted_member_list'].append(curr_user)
                # print 'seems no error!'

                es.index(index='events', doc_type='default', id=event_id, body=curr_event_info)
        es.index(index='users', doc_type='default', id=curr_user, body=curr_user_info)
    return render_template('main_event_status.html')

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
        userId_list = []
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
        pending_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['pending_friend_requests']
        print pending_friend_list
        for user in pending_friend_list:
            print(user)
            friendreq = es.get(index='users', doc_type='default', id=user)
            userId_list.append([friendreq['_id'], friendreq['_source']['firstname'], friendreq['_source']['lastname'], friendreq['_source']['phone']])
        return render_template("ViewPendingFriendRequest.html", **dict(data=userId_list))
    if request.method == 'POST':
        friendIds = request.form.getlist('FriendId')
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        for userId in friendIds:
            user_info = es.get(index='users', doc_type='default', id=userId)['_source']
            user_info['friends'].append(curr_user)
            if curr_user in user_info['pending_sent_requests']:
                user_info['pending_sent_requests'].remove(curr_user)
            es.index(index='users', doc_type='default', id=userId, body=user_info)

            user_info = es.get(index='users', doc_type='default', id=curr_user)['_source']
            user_info['friends'].append(userId)
            if userId in user_info['pending_friend_requests']:
                user_info['pending_friend_requests'].remove(userId)
            es.index(index='users', doc_type='default', id=curr_user, body=user_info)
        return render_template('homepage.html')

@application.route("/viewfriends", methods=['GET', 'POST'])
def viewfriends():
    userId_list = []
    if request.method == 'GET':
        if 'curr_userid' in session:
          curr_user = session['curr_userid']
          friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        for user in friend_list:
             friend = es.get(index='users', doc_type='default', id=user)
             userId_list.append([friend['_id'], friend['_source']['firstname'], friend['_source']['lastname'], friend['_source']['phone']])
        return render_template("FriendList.html", **dict(data=userId_list))
   
@application.route("/addfriends", methods=['GET', 'POST'])
def add_friend():
    if request.method == 'GET':
       
        all_users = es.search(index='users', body={"query": {"match_all": {}}})['hits']['hits']
        # print all_users
        userId_list = []
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_pend = es.get(index='users', doc_type='default', id=curr_user)['_source']['pending_sent_requests']
        # print curr_pend
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
        # print curr_user_info['pending_sent_requests']
        es.index(index='users', doc_type='default', id=curr_user, body=curr_user_info)
        # print "hhah"
        return render_template('homepage.html')
    return render_template("AddFriends.html")


@application.route("/create_event", methods=['GET', 'POST'])
def create_event():
    event_form = request.form.to_dict()
    # print event_form
    if request.method == 'GET':
        userId_list = []
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        for user in curr_friend_list:
            user_info = es.get(index='users', doc_type='default', id=user)['_source']
            userId_list.append([user_info['userId'], user_info['firstname'], user_info['lastname']])
        return render_template("create_event.html", **dict(friend=userId_list))
    if request.method == 'POST':
        coor = request.form.to_dict()
        if 'check' in coor and coor['check'] == 'true':
            lat = coor["lat"]
            lng = coor["lng"]
            query = "curl -XGET https://search-shoppingmall-qneri4bfel2dfgjpqq453wilcq.us-east-1.es.amazonaws.com/shoppingmall2/location/_search -d" + " '" + '{"query":{"bool":{"must":{"match_all":{}},"filter":{"geo_distance":{"distance":"1km","pin.location":{"lat":' + str(
                lat) + ',"lon":' + str(lng) + '}}}}}}' + "'" + " -H 'Content-Type: application/json'"
            # print query

            t = Popen(query, shell=True, stdout=PIPE)
            text = t.communicate()[0]
            # print text
            tmp = json.loads(text)
            malls = json.loads(text)["hits"]["hits"]
            data = []
            for mall in malls:
                item = dict()
                item["name"] = mall["_source"]["name"]
                if "rating" in mall["_source"]["content"]:
                    item["rating"] = mall["_source"]["content"]["rating"]
                if "price_level" in mall["_source"]["content"]:
                    item["price_level"] = mall["_source"]["content"]["rating"]
                item["location"] = mall["_source"]["pin"]["location"]
                data.append(item)

            # print json.dumps(data, indent=4)
            result = json.dumps(data)
            return result
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        members = request.form.getlist('memberlist')
        # print members
        # print type(members)
        members2 = []
        friend_members = []
        all_users = es.search(index='users', body={"query": {"match_all": {}}})['hits']['hits']
        curr_friend_list = es.get(index='users', doc_type='default', id=curr_user)['_source']['friends']
        event_information = {}
        event_information['event_name'] = event_form['eventName']
        if es.exists(index='events', doc_type='default', id=event_information['event_name']):
            return render_template('create_event.html', error='event already exists')
        event_information['event_time'] = event_form['eventTime']
        event_information['event_host'] = curr_user
        event_information['location'] = 'somewhere'
        event_information['accepted_member_list'] = []
        # print 'linyihan'
        if members[-1] == "alluser":
            for i in range(len(members) - 1):
                friend_members.append(members[i])
            members2 = [friend_members[i] for i in range(len(friend_members)-1)]
            for user in all_users:
                user = user['_id']
                if user not in curr_friend_list:
                    if user != curr_user:
                        members2.append(user)
                        event_information['pending_member_list'] = members2
        else:
            event_information['pending_member_list'] = members
        event_information['member_list'] = event_information['pending_member_list']
        es.index(index="events", doc_type="default", id=event_form['eventName'], body=event_information)

        for invited_user in event_information['member_list']:
            invited_user_body = es.get(index='users', doc_type='default', id=invited_user)['_source']
            invited_user_body['invited_events'].append(event_information['event_name'])
            es.index(index='users', doc_type='default', id=invited_user, body=invited_user_body)

        # print es.get(index='events', doc_type='default', id=event_form['eventName'])
        return redirect('/homepage')
    return render_template('create_event.html')

@application.route('/event_status_detail', methods=['GET', 'POST'])
def event_status_detail():
    if request.method == 'GET':
        curr_user = ''
        if 'curr_userid' in session:
            curr_user = session['curr_userid']
        all_events = es.search(index='events', body={"query": {"match_all":{}}})['hits']['hits']
        return_list = []
        for event in all_events:
            if event['_source']['event_host'] == curr_user:
                curr_dict = {}
                curr_dict['event_name'] = event['_id']
                curr_dict['event_time'] = event['_source']['event_time']
                curr_dict['event_location'] = event['_source']['location']
                curr_dict['event_member_status'] = {'pending':[], 'accepted':[], 'declined':[]}
                for member in event['_source']['member_list']:
                    if member in event['_source']['pending_member_list']:
                        curr_dict['event_member_status']['pending'].append(member)
                    elif member in event['_source']['accepted_member_list']:
                        curr_dict['event_member_status']['accepted'].append(member)
                    else:
                        curr_dict['event_member_status']['declined'].append(member)
                return_list.append(curr_dict)
    return render_template('event_status_detail.html', **dict(alldata=return_list))

@application.route('/logout',methods=['GET','POST'])
def logout():
    if 'curr_userid' in session:
        session['curr_userid'] = None
    return render_template('weshop.html')

if __name__ == '__main__':
    application.run()
    # print es.get(index='events', doc_type='default', id='haha')

    # es.delete_by_query(index='events', body={'query':{'match_all':{}}})
    # es.delete_by_query(index='users', body={'query': {'match_all': {}}})
