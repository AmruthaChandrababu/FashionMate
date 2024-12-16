from pymongo import MongoClient

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['Fashion']
    

    def register_user(self, user):
        users_collection = self.db['users']
        users_collection.insert_one(user.to_dict())

    def get_user(self, username):
        users_collection = self.db['users']
        return users_collection.find_one({'username': username})
    
    def insert_wardrobe_item(self, username, item):
        wardrobe_collection = self.db['wardrobe']
        item['user_id'] = username
        return wardrobe_collection.insert_one(item)




    def get_user_wardrobe(self, username):
        wardrobe_collection = self.db['wardrobe']
        return list(wardrobe_collection.find({'user_id': username}))
    
    
