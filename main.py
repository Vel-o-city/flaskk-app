from flask import Flask, render_template, request, jsonify
import requests
import pymongo
from util import fetch_data,get_conversations_for_user
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
connectionString = "mongodb://65.2.116.84:27017/"
client = pymongo.MongoClient(connectionString)
db = client['production']
url_data='https://napi.prepseed.com/chats/getCustomFilterData?client=63ecdbe09465911b205459fe'
url_sign='https://napi.prepseed.com/users/signin'

def is_user_active(last_message_time, active_span):
    try:
        if last_message_time == None:
             return False
        else:
            timestamp_milliseconds = last_message_time
            timestamp_seconds = timestamp_milliseconds / 1000
            last_message_datetime = pd.to_datetime(timestamp_seconds, unit='s',utc=True)
    except ValueError:
        return False
    
    # Map active span to timedelta
    if active_span == 'Last 24 Hours':
        active_duration = pd.Timedelta(days=1)
    elif active_span == 'Last 48 Hours':
        active_duration = pd.Timedelta(days=2)
    elif active_span == 'Last 72 Hours':
        active_duration = pd.Timedelta(days=3)
    else:
        return False  # Invalid active span
    
    current_datetime = pd.Timestamp.now(tz='UTC')
    last_active_datetime = current_datetime - active_duration
    return last_message_datetime >= last_active_datetime

data={
    "user":
    {
    "email": "prepseed-user@prepseed.com",
    "password": "user@123"
    },
    "portal":"preparation"
}
resp=requests.post(url_sign, json=data).json()
token=resp['token']
headers = {
    'Content-Type': 'application/json',
    'authorization': f'Token {token}'
}

response=requests.get(url_data,headers=headers)
x=response.json()
# Sample user data (expanded)
users = fetch_data()

def fetch_branches_and_batches():
        data = x.get("data", [])
        branches = [option for item in data if item.get("filterName") == "Branch" for option in item.get("options", [])]
        batches = [option for item in data if item.get("filterName") == "Batch" for option in item.get("options", [])]
        return branches, batches
# Function to filter user data based on branches and batches
def filter_users(branches, batches,roles,tenture):
    filtered_users = users
    if tenture != '':
        for user in filtered_users:
            user["active_status"] = is_user_active(user['last_message_time'], tenture)


    if branches != '':
        filtered_users = [user for user in filtered_users if any(branch in user.get('branches', []) for branch in branches.split(','))]
        
    if batches != '':
        filtered_users = [user for user in filtered_users if any(batch in user.get('batches', []) for batch in batches.split(','))]

    if roles !='':
        filtered_users=[user for user in filtered_users if user.get('role', '') == roles]
    return filtered_users

@app.route('/')
def index():
    all_branches,all_batches=fetch_branches_and_batches()
    all_roles=['moderator','mentor','user','parent','Faculty']
    all_tentures=['Last 24 Hours','Last 48 Hours','Last 72 Hours']
    return render_template('index.html', branches=all_branches, batches=all_batches,roles=all_roles,tentures=all_tentures)

@app.route('/get_users', methods=['GET'])
def get_users():
    branches = request.args.get('branch', '')
    batches = request.args.get('batch', '')
    roles = request.args.get('role', '')
    tentures=request.args.get('tenture','')
    filtered_users = filter_users(branches, batches,roles,tentures)
    return jsonify(filtered_users)

# conversation_data = {
#     'user1@example.com': [
#         {'name': 'Group 1', 'total_messages': 100, 'messages_by_role': {'Admin': 30, 'User': 50, 'Manager': 20}, 'messages_by_user': 25},
#         {'name': 'Group 2', 'total_messages': 200, 'messages_by_role': {'Admin': 60, 'User': 100, 'Manager': 40}, 'messages_by_user': 40},
#     ],
#     'user2@example.com': [
#         {'name': 'Group 3', 'total_messages': 150, 'messages_by_role': {'Admin': 20, 'User': 80, 'Manager': 50}, 'messages_by_user': 60},
#         {'name': 'Group 4', 'total_messages': 300, 'messages_by_role': {'Admin': 80, 'User': 150, 'Manager': 70}, 'messages_by_user': 90},
#     ],
# }

# @app.route('/get_user_details', methods=['GET'])
# def get_user_details():
#     email = request.args.get('email')
#     for user in users:
#         for key, value in user.items():
#             if key == 'email' and value == email:
#                 # Once found, retrieve the value associated with the "user" field
#                 user_value = user['user']
#                 break
#     conversation_names=get_conversations_for_user(user_value)
#     if user:
#         return jsonify(conversation_data['user1@example.com'])
#     else:
#         return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)