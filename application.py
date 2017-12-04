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
    if request.form['type'] == 'login':  # an existing user is going to log in
        if not es.exists(index="users", doc_type="default", id=request.form['userId']):
            return jsonify({'status': 'failed', 'message': 'user does not exist'})
        else:
            user_info = es.get(index="users", doc_type="default", id=request.form['userId'])
            if user_info['_source']['password'] == request.form['info']['password']:
                pass
                return_json = user_info['_source']
                return_json.pop('password')
                return_json['status'] = 'success'

                # do something to return the event that most likely to be attended by the user

                return jsonify(return_json)
            else:
                return jsonify({'status': 'failed', 'message': 'incorrect password'})

    elif request.form['type'] == 'signup':  # a new user is going to sign up a new account
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

    elif request.form['type'] == 'create_event':
        pass
    elif request.form['type'] == 'attend_event':  # a user agrees to attend a event
        pass
    elif request.form['type'] == 'add_friend':  # user1 sends friend request to user2
        if not es.exists(index="users", doc_type="default", id=request.form['info']['user2']):
            return jsonify({"status": "failed", "message": "user2 does not exist"})
        else:
            user_info = es.get(index="users", doc_type="default", id=request.form['info']['user2'])['_source']
            user_info['pending_friend_requests'].append(request.form['info']['user1'])
            es.index(index="users", doc_type="default", id=request.form['info']['user2'], body=user_info)
            return jsonify({"status": "succeed", "message": "friend request sent"})
    elif request.form['type'] == 'add_friend_agree':  # user2 agrees to be friend with user1
        user_info = es.get(index="users", doc_type="default", id=request.form['info']['user2'])['_source']
        if request.form['info']['user1'] in user_info['pending_friend_requests']:
            user_info['pending_friend_requests'].remove(request.form['info']['user1'])
        user_info['friends'].append(request.form['info']['user1'])
        es.index(index="users", doc_type="default", id=request.form['info']['user2'], body=user_info)
        return({'status': 'succ'})

    elif request.form['type'] == 'add_friend_decline':  # user2 declines to be friend with user1
        user_info = es.get(index="users", doc_type="default", id=request.form['info']['user2'])['_source']
        if request.form['info']['user1'] in user_info['pending_friend_requests']:
            user_info['pending_friend_requests'].remove(request.form['info']['user1'])
        es.index(index="users", doc_type="default", id=request.form['info']['user2'], body=user_info)

    return render_template('main_page.html')

if __name__ == '__main__':
    application.run()
