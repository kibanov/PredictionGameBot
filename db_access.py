import pymongo
from datetime import datetime, timedelta

from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)
eurodb = client.euro16
predictions_collection = eurodb.predictions
matches_collection = eurodb.matches

# ADD USER:
def add_user(uid):
    try:
        user_search = predictions_collection.count({"user_id": uid})
        if user_search == 0:
            post = {"user_id": uid}
            user_id = predictions_collection.insert_one(post).inserted_id
        else:
            existing_user = predictions_collection.find_one({"user_id": uid})
            user_id = existing_user.get('_id')
        return (user_id)
    except Exception as e:
        return(0)

def add_prediction(uid, matchid, winner, goals, total):
    result = predictions_collection.update_one({"user_id": uid}, {"$addToSet": {"predicted_matches" : matchid}})
    result2 = predictions_collection.update_one(
    	{"user_id": uid},
    	{
    	    "$addToSet": {
    	        "predictions":
                    { "match_no": matchid,
                    "winner": winner,
                    "goals": goals,
                    "total": total}
            }
        }, upsert=True)
    return (result)


def add_name(uid, uname):
	result = predictions_collection.update_one(
		{"user_id": uid},
		{"$set": {"name" : uname}})

def add_group(uid, group):
    result = predictions_collection.update_one(
        {"user_id": uid},
        {"$addToSet": {"groups" : group}})

def get_next_match(uid):
    active_matchs = list(matches_collection.find({"active" : 1},{"match_no" : 1, "_id" : 0}))
    if(len(active_matchs[0]) == 0):
        return(0)
    predicted_matches = list(predictions_collection.find({"user_id" : uid},{"predicted_matches" : 1, "_id" : 0}))
    active_match_ids = [c['match_no'] for c in active_matchs]
    if (len(predicted_matches[0]) > 0):
        relevant_matches = [c for c in active_match_ids if c not in predicted_matches[0]['predicted_matches']]
    else:
    	relevant_matches = active_match_ids
    if(len(relevant_matches) == 0):
        return(0)
    next_match_id = sorted(relevant_matches)[0]
    next_match = list(matches_collection.find({"match_no" : next_match_id},{"_id" : 0}))
    return(next_match)

def refresh_match(dt):
    res = matches_collection.update({ "date" : {"$lte": dt}}, {"$set" : {"active" : 0}}, multi=True)
    print(str(dt) + ': ' + str(res))    

def get_all_users():
    all_users = list(predictions_collection.find({},{"_id" :0}))
    return (all_users)

def get_all_users_ids():
    all_users = get_all_users()
    all_users_ids = [c['user_id'] for c in all_users]
    return (all_users_ids)

def get_user(uid):
    users = list(predictions_collection.find({"user_id" : uid},{"_id" : 0}))
    if (len(users) > 0):
        return(users[0])
    else:
        return 0

def matches_to_start_till(dt):
    res = list(matches_collection.find({"date" : {"$lte": dt}}))
    return(res)

def today_matches():
    end_of_day = datetime.now().replace(hour = 23, minute = 59, second = 59)
    start_of_day = datetime.now().replace(hour = 00, minute = 00, second = 1)
    res = list(matches_collection.find({"date" : {"$lte": end_of_day, "$gte": start_of_day}}))
    return(res)


# UPDATE USER:
def update_user(id):
    return ()

# ADD PREDICTION:
# def add_prediction(user_id, match_no, winner, goals, total):
    # conncet to mongo
    # check if the 

# EDIT PREDICTION: