class User:
    def __init__(self, username, password, preferences):
        self.username = username
        self.password = password
        self.preferences = preferences

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'preferences': self.preferences
        }
