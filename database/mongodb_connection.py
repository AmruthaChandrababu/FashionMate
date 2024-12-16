from pymongo import MongoClient
import os
from dotenv import load_dotenv

class MongoDBConnection:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # MongoDB connection parameters
        self.MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'fashionmate')
        
        # Establish connection
        try:
            self.client = MongoClient(self.MONGO_URI)
            self.db = self.client[self.DATABASE_NAME]
            print("MongoDB connection successful!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
    
    def get_collection(self, collection_name):
        """
        Get a specific collection from the database
        
        Args:
            collection_name (str): Name of the collection
        
        Returns:
            pymongo.collection.Collection: MongoDB collection
        """
        return self.db[collection_name]
    
    def insert_user(self, user_data):
        """
        Insert a new user into the users collection
        
        Args:
            user_data (dict): User information to be inserted
        
        Returns:
            str: Inserted user's ID
        """
        users_collection = self.get_collection('users')
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def insert_wardrobe_item(self, user_id, item_data):
        """
        Insert a new wardrobe item for a specific user
        
        Args:
            user_id (str): ID of the user
            item_data (dict): Wardrobe item details
        
        Returns:
            str: Inserted item's ID
        """
        wardrobe_collection = self.get_collection('wardrobe')
        item_data['user_id'] = user_id
        result = wardrobe_collection.insert_one(item_data)
        return str(result.inserted_id)
    
    def get_user_wardrobe(self, user_id):
        """
        Retrieve all wardrobe items for a specific user
        
        Args:
            user_id (str): ID of the user
        
        Returns:
            list: List of wardrobe items
        """
        wardrobe_collection = self.get_collection('wardrobe')
        return list(wardrobe_collection.find({'user_id': user_id}))
    
    def close_connection(self):
        """
        Close the MongoDB connection
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

# Example usage
if __name__ == '__main__':
    # Initialize MongoDB connection
    mongo_conn = MongoDBConnection()
    
    # Example: Insert a user
    user_data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'preferences': {
            'style': 'casual',
            'color_preferences': ['blue', 'gray']
        }
    }
    user_id = mongo_conn.insert_user(user_data)
    
    # Example: Insert a wardrobe item
    wardrobe_item = {
        'type': 'shirt',
        'color': 'blue',
        'brand': 'Nike',
        'category': 'Top'
    }
    item_id = mongo_conn.insert_wardrobe_item(user_id, wardrobe_item)
    
    # Close connection
    mongo_conn.close_connection()