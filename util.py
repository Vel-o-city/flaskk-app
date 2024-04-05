import pymongo
import pandas as pd
from bson import ObjectId
import json

def fetch_data():
    connectionString = "mongodb://65.2.116.84:27017/"
    client = pymongo.MongoClient(connectionString)
    db = client['production']
    collection1 = db['users']
    pipeline1 = [
        {
            "$match": {
                "client": {
                    "$in": [
                        ObjectId("63ecdbe09465911b205459fe"),
                        "63ecdbe09465911b205459fe"
                    ]
                }
            }
            },
            {
                "$project":{
                    "_id":1,
                    "name":1,
                    "email":1,
                    "phases":1,
                    "sections":1,
                    "role":1
            }
        }
    ]
    user_df = pd.DataFrame(collection1.aggregate(pipeline1))
    collection2 = db['phases']
    fields = {"_id":1,"name":1}
    phases_df = pd.DataFrame(collection2.find({},fields))
    # Convert '_id' column in 'branches' DataFrame to string for matching
    phases_df['_id'] = phases_df['_id'].astype(str)
    users=user_df['_id'].tolist()
    # Map ObjectIds to branchnames in 'myusers' DataFrame
    user_df['phases'] = user_df['phases'].apply(lambda x: [phases_df.loc[phases_df['_id'] == str(oid), 'name'].values[0] for oid in x])
    user_df = user_df.rename(columns={'phases': 'branches','sections':'batches','_id':'user'})
    collection3=db['userlastlogins']
    fields={"user":1,"date":1,"_id":0}
    last_log=pd.DataFrame(collection3.find({},fields))
    merged_df=pd.merge(user_df,last_log,on='user',how='left')
    merged_df['last_login'] = pd.to_datetime(merged_df['date']).dt.strftime('%H:%M %d/%m/%y')
    merged_df.drop(columns=['date'],inplace=True)
    collection4=db['messages']
    pipeline = [
        {"$match": {"sender": {"$in": users}}},  # Uncomment if you want to filter specific users
        {"$group": {"_id": "$sender", "last_message": {"$max": "$createdAt"}}},
        {"$project": {"_id": 0, "user_id": "$_id", "last_message_timestamp": "$last_message"}},
    ]
    cursor = list(collection4.aggregate(pipeline))
    active_df=pd.DataFrame(cursor)
    merged_time_df = pd.merge(merged_df, active_df, how='left', left_on='user', right_on='user_id')
    merged_time_df.rename(columns={'last_message_timestamp': 'last_message_time'}, inplace=True)
    merged_time_df['last_message_time'] = pd.to_datetime(merged_time_df['last_message_time'])
    merged_time_df.drop(columns={'user_id'},inplace=True)
    merged_time_df['user'] = merged_time_df['user'].astype(str)
    json_data = merged_time_df.to_json(orient='records')
    json_data=json.loads(json_data)
    return json_data

def get_conversations_for_user(user_id):
    connectionString = "mongodb://65.2.116.84:27017/"
    client = pymongo.MongoClient(connectionString)
    db = client['production']
    collection=db['conversations']
    pipeline = [
        {"$unwind": "$users"},
        {"$match": {"users.user": ObjectId(user_id)}}
    ]
    conversations = collection.aggregate(pipeline)

    conversation_names = []
    for conversation in conversations:
        conversation_names.append(conversation['_id'])  # Assuming 'name' is the field containing conversation names

    return conversation_names