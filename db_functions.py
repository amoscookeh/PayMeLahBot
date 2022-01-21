from pymongo import MongoClient
from datetime import date
import os

PASSWORD = os.environ['MONGO_PASSWORD']
client = MongoClient(
    'mongodb+srv://amos:{}@paymecluster.ktr8w.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'.format(PASSWORD))
db = client.paymelah_database
collection = db.user_collection


# Helpers
def create_new_user_record(username):
    post = {
        "_id": username,
        "activity_count": 0,
        "receipt_data": []
    }
    response = collection.insert_one(post)
    print(response)
    response = update_unique_user()
    print(response)



def add_receipt_data(username, receipt_data):
    data = {
        str(date.today()): receipt_data
    }

    response = collection.update_one(
        {"_id": username},
        {"$push": {"receipt_data": data}}
    )
    print(response)


def user_exists(username):
    return collection.count_documents({"_id": username}) > 0


def find_user(username):
    return collection.find_one({'_id': {"$in": username}})


def update_user_activity(username):
    response = collection.update_one(
        { "_id": username },
        { "$inc": { "activity_count": 1 } }
    )
    print(response)


def update_total_activity():
    response = collection.update_one(
        { "_id": "global" },
        { "$inc": { "total_usage": 1 } }
    )
    print(response)


def update_unique_user():
    response = collection.update_one(
        { "_id": "global" },
        { "$inc": { "unique_user": 1 } }
    )
    print(response)


def get_total_activity():
    return collection.find_one(
        {"_id": "global"}
    )