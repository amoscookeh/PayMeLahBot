from pymongo import MongoClient
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
    response = collection.updateOne(
        {"_id": username},
        {"$push": {"receipt_data": receipt_data}}
    )
    print(response)


def user_exists(username):
    return collection.count_documents({"_id": username}) > 0


def find_user(username):
    return collection.find_one({'_id': {"$in": username}})


def update_user_activity(username):
    response = collection.updateOne(
        { "_id": username },
        { "$inc": { "activity_count": 1 } }
    )
    print(response)


def update_total_activity():
    response = collection.updateOne(
        { "_id": "global" },
        { "$inc": { "total_usage": 1 } }
    )
    print(response)


def update_unique_user():
    response = collection.updateOne(
        { "_id": "global" },
        { "$inc": { "unique_user": 1 } }
    )
    print(response)


def get_total_activity():
    return collection.find_one(
        {"_id": "global"}
    )