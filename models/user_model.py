class User:
    def __init__(self, username, password, preferences=None, 
                 city=None, country=None, favorite_colors=None, clothing_items=None, measurements=None):
        self.username = username
        self.password = password
        self.password = password
        self.preferences = preferences or []
        self.city = city
        self.country = country
        self.favorite_colors = favorite_colors or []
        self.clothing_items = clothing_items or []
        self.measurements = measurements or {}

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'preferences': self.preferences,
            'city': self.city,
            'country': self.country,
            'favorite_colors': self.favorite_colors,
            'clothing_items': self.clothing_items,
            'measurements': self.measurements
        }
