from pymongo import MongoClient
from bson import ObjectId

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['Fashion_Mate']

    def register_user(self, user):
        users_collection = self.db['users']
        users_collection.insert_one(user.to_dict())

    def get_user(self, username):
        users_collection = self.db['users']
        return users_collection.find_one({'username': username})

    def insert_wardrobe_item(self, user_id, item):
        collection = self.db['wardrobe']
        item["user_id"] = user_id
        result = collection.insert_one(item)
        return result.inserted_id
    def update_user_location(self, username, city, country):
        users_collection = self.db['users']
        users_collection.update_one(
            {'username': username},
            {'$set': {'city': city, 'country': country}}
        )

    def get_user_wardrobe(self, user_id):
        wardrobe_collection = self.db['wardrobe']
        items = list(wardrobe_collection.find({'user_id': user_id}))
        for item in items:
            item['_id'] = str(item['_id'])
        return items
