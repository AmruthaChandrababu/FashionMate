from flask import Flask,send_from_directory, render_template, jsonify, request,redirect,url_for,session
from flask_pymongo import PyMongo
import requests
import pandas as pd
import os
from PIL import Image 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database.mongo_conn import MongoDBConnection
from models.user_model import User
from models import hf_classifier
import os
import datetime
from rembg import remove
from PIL import Image
import io

app = Flask(__name__, template_folder='assets/templates', static_folder='assets/static')

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Fashion_Mate"
mongo = PyMongo(app)

# Static folder for images
STATIC_FOLDER = "assets/static/images"
RESIZED_FOLDER = "static/resized_images"
app.secret_key = 'supersecretkey'
OPENWEATHER_API_KEY = 'e7f6a61398d961be542c9f01ded592aa'

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'assets', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# MongoDB connection
mongo_conn = MongoDBConnection()
# Load the dataset
try:
    dataset = pd.read_csv("cleaned_styles.csv")
    dataset = dataset[
        (dataset['masterCategory'] == 'Apparel') &
        (dataset['subCategory'] != 'Innerwear')
        ]
except Exception as e:
    print(f"Error loading dataset: {e}")
    dataset = pd.DataFrame()

def resize_images(image_paths, output_folder, size=(30, 40)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            img = img.resize(size, Image.ANTIALIAS)
            img.save(os.path.join(output_folder, os.path.basename(image_path)))
        except Exception as e:
            print(f"Error resizing image {image_path}: {e}")    



@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register.html', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Personal info
        username = request.form['username']
        
        password = generate_password_hash(request.form['password'])
        
        # Style preferences
        preferences = request.form.getlist('preferences')
        
        # Location information
        city = request.form['city']
        country = request.form['country']
        
        # Colors (optional)
        favorite_colors = request.form.getlist('favorite_colors')
        
        # Clothing preferences
        clothing_items = request.form.getlist('clothing_items')
        
        # Body measurements (optional)
        measurements = {
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'chest': request.form.get('chest'),
            'waist': request.form.get('waist'),
            'hips': request.form.get('hips')
        }
        
        # Filter out empty measurements
        measurements = {k: v for k, v in measurements.items() if v}
        
        # Check if user exists
        if mongo_conn.get_user(username):
            return "User with this username already exists!"

        # Register user with all form data
        user = User(
            username=username,
            password=password,
            preferences=preferences,
            city=city,
            country=country,
            favorite_colors=favorite_colors,
            clothing_items=clothing_items,
            measurements=measurements
        )
        
        mongo_conn.register_user(user)
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = mongo_conn.get_user(username)
        
        if not user or 'password' not in user or not check_password_hash(user['password'], password):
            # For AJAX requests, return JSON error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Invalid username or password!"}), 401
            # For normal requests, return error message
            return "Invalid username or password!", 401
        
        session['user'] = username
        
        # For AJAX requests, return success with redirect URL
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "redirect": url_for('index')})
        
        # For normal requests, redirect
        return redirect(url_for('index'))
    
    return render_template('login.html')
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

@app.route("/my_wardrobe")
def my_wardrobe():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("MyWardrobe.html")

@app.route('/wardrobe_data', methods=["GET"])
def fetch_wardrobe_data():
    if 'user' not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session['user']
    wardrobe_items = mongo_conn.get_user_wardrobe(user_id)

    grouped_items = {}
    for item in wardrobe_items:
        category = item.get("classification", {}).get("category", "Unknown")
        item["_id"] = str(item["_id"])
        grouped_items.setdefault(category, []).append(item)

    return jsonify(grouped_items)





def process_image(image_path):
    try:
        # Open the image file
        with open(image_path, "rb") as image_file:
            input_image = image_file.read()

        # Remove background
        output_image = remove(input_image)

        # Convert to Pillow image
        image = Image.open(io.BytesIO(output_image)).convert("RGBA")

        # Resize to a uniform dimension
        uniform_size = (400, 400)
        image = image.resize(uniform_size, Image.Resampling.LANCZOS)

        # Add a white background if needed (optional, for better display)
        background = Image.new("RGBA", uniform_size, (255, 255, 255, 255))
        background.paste(image, (0, 0), image)

        # Save the processed image back
        background.save(image_path, format="PNG")
    except Exception as e:
        print(f"Error in process_image: {str(e)}")

@app.route('/update_location', methods=['POST'])
def update_location():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    city = request.form.get('city')
    country = request.form.get('country')
    
    if not city or not country:
        return "City and country are required!", 400
    
    # Update user location in database
    mongo_conn.update_user_location(session['user'], city, country)
    
    return redirect(url_for('profile'))
@app.route('/upload_item', methods=["POST"])
def upload_wardrobe_item():
    try:
        if 'user' not in session:
            return jsonify({"error": "Unauthorized access"}), 403

        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({"error": "No file uploaded"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image (remove background and resize)
        process_image(filepath)

        # Classify the image
        classification_result = hf_classifier.classify_image(filepath)

        # Store wardrobe item
        wardrobe_item = {
            "filename": filename,
            "image_path": url_for('uploaded_file', filename=filename),
            "user_id": session['user'],
            "upload_date": datetime.datetime.now().isoformat(),
            "classification": classification_result,
        }

        # Insert into MongoDB and get the inserted ID
        inserted_id = mongo_conn.insert_wardrobe_item(session['user'], wardrobe_item)

        # Add the string version of the ObjectId to the wardrobe_item
        wardrobe_item["_id"] = str(inserted_id)

        return jsonify({"message": "Item uploaded successfully", "item": wardrobe_item})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred while uploading the item: {str(e)}"}), 500

# Serve images from the uploads directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_weather(city, country):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'condition': data['weather'][0]['main'],
                'humidity': data['main']['humidity'],
                'city': city
            }
        return None
    except Exception as e:
        print(f"Error fetching weather: {str(e)}")
        return None

import datetime

def get_weather_based_recommendations(weather, wardrobe_items):
    # Get current timestamp for 12-hour rotation
    current_time = datetime.datetime.now()
    rotation_period = current_time.replace(hour=current_time.hour - (current_time.hour % 12), 
                                         minute=0, second=0, microsecond=0)
    # Create a seed for consistent but rotating selection
    rotation_seed = int(rotation_period.timestamp() / (12 * 3600))  # Changes every 12 hours
    
    temp = weather['temperature']
    condition = weather['condition'].lower()
    
    # Define clothing categories for different weather conditions
    WARM_TOPS = ['Sweater', 'Turtleneck', 'Flannel', 'Henley']
    LIGHT_TOPS = ['Tee', 'Tank', 'Blouse', 'Top', 'Button-Down', 'Halter']
    WARM_OUTERWEAR = ['Coat', 'Peacoat', 'Parka', 'Bomber', 'Hoodie']
    LIGHT_OUTERWEAR = ['Blazer', 'Cardigan', 'Kimono']
    RAIN_GEAR = ['Anorak', 'Jacket']
    WARM_BOTTOMS = ['Jeans', 'Sweatpants', 'Joggers']
    LIGHT_BOTTOMS = ['Shorts', 'Skirt', 'Culottes', 'Capris']
    FULL_BODY = ['Dress', 'Jumpsuit', 'Romper']
    
    recommendations = []
    weather_note = ""
    required_categories = []

    # Temperature-based recommendations
    if temp < 10:  # Very Cold (Below 10°C)
        weather_note = "It's very cold! Layer up with warm clothing."
        required_categories = [
            ('warm_top', WARM_TOPS, "a warm top"),
            ('warm_outerwear', WARM_OUTERWEAR, "a warm outer layer"),
            ('warm_bottom', WARM_BOTTOMS, "warm bottoms")
        ]
        
    elif 10 <= temp < 18:  # Cool (10-18°C)
        weather_note = "Cool weather - perfect for light layering."
        required_categories = [
            ('light_top', LIGHT_TOPS, "a light top"),
            ('light_outerwear', LIGHT_OUTERWEAR + WARM_OUTERWEAR, "a light jacket or cardigan"),
            ('bottom', WARM_BOTTOMS, "comfortable bottoms")
        ]
        
    elif 18 <= temp < 25:  # Moderate (18-25°C)
        weather_note = "Pleasant temperature - great for most clothing options."
        required_categories = [
            ('top', LIGHT_TOPS, "a comfortable top"),
            ('bottom', LIGHT_BOTTOMS + WARM_BOTTOMS, "suitable bottoms"),
            ('optional_layer', LIGHT_OUTERWEAR, "a light layer for evening")
        ]
        
    else:  # Hot (25°C and above)
        weather_note = "Hot weather - choose light, breathable clothing."
        required_categories = [
            ('light_top', LIGHT_TOPS, "a breathable top"),
            ('light_bottom', LIGHT_BOTTOMS, "light bottoms")
        ]
        # Add option for full-body items in hot weather
        if any(item['classification']['label'] in FULL_BODY for item in wardrobe_items):
            required_categories.append(('full_body', FULL_BODY, "a breezy dress or romper"))

    # Weather condition modifiers
    if 'rain' in condition or 'drizzle' in condition:
        weather_note += " Don't forget rain protection!"
        required_categories.insert(0, ('rain_gear', RAIN_GEAR, "rain protection"))
    elif 'snow' in condition:
        weather_note += " Snowfall expected - prioritize warm, waterproof layers!"
        required_categories.insert(0, ('warm_outerwear', WARM_OUTERWEAR, "a warm, protective coat"))
    elif 'thunderstorm' in condition:
        weather_note += " Stormy conditions - bring weatherproof outerwear!"
        required_categories.insert(0, ('rain_gear', RAIN_GEAR, "waterproof protection"))
    elif 'cloudy' in condition and temp < 20:
        weather_note += " Cloudy and cool - an extra layer might be nice."
        if not any(cat[0] == 'light_outerwear' for cat in required_categories):
            required_categories.append(('light_outerwear', LIGHT_OUTERWEAR, "a light layer"))

    # Find matching items from wardrobe with rotation
    selected_items = []
    missing_items = []

    for category_type, category_options, category_description in required_categories:
        matching_items = [
            item for item in wardrobe_items 
            if item['classification']['label'] in category_options
        ]
        
        if matching_items:
            # Sort items to ensure consistent ordering
            matching_items.sort(key=lambda x: x['classification']['label'])
            
            # Use rotation seed to select different items every 12 hours
            selection_index = (rotation_seed + len(selected_items)) % len(matching_items)
            selected_items.append(matching_items[selection_index])
        else:
            missing_items.append(category_description)

    # Update weather note with missing items
    if missing_items:
        weather_note += f"\nConsider adding {', '.join(missing_items)} to your wardrobe for this weather."

    # Add time period to weather note
    period = "morning to afternoon" if current_time.hour < 12 else "evening to night"
    weather_note = f"{weather_note}"

    return {
        'items': selected_items,
        'weatherNote': weather_note,
        'missing': missing_items,
        'rotationPeriod': rotation_period.strftime("%Y-%m-%d %H:00"),
        'nextRotation': (rotation_period + datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:00")
    }
@app.route('/weather_recommendations')
def weather_recommendations():
    if 'user' not in session:
        return jsonify({"error": "User not logged in"}), 403
    
    user = mongo_conn.get_user(session['user'])
    
    # Check if user has location information
    if not user.get('city') or not user.get('country'):
        return jsonify({
            "error": "Location not set",
            "message": "Please update your location in your profile"
        }), 400
    
    weather = get_weather(user['city'], user['country'])
    
    if not weather:
        return jsonify({"error": "Unable to fetch weather data"}), 500
    
    wardrobe_items = mongo_conn.get_user_wardrobe(session['user'])
    recommendations = get_weather_based_recommendations(weather, wardrobe_items)
    
    return jsonify({
        "weather": weather,
        "recommendations": recommendations
    })


@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = mongo_conn.get_user(session['user'])
    return render_template('Profile.html', user=user)

@app.route("/save_preferences", methods=["POST"])
def save_preferences():
    data = request.json
    username = data.get("username")
    if username:
        mongo.db.user_preferences.update_one(
            {"username": username},
            {"$set": {"preferences": data.get("preferences", {})}},
            upsert=True,
        )
        return jsonify({"message": "Preferences saved successfully!"})
    return jsonify({"message": "Username not provided!"}), 400

@app.route("/get_recommendations", methods=["GET"])
def get_recommendations():
    username = request.args.get("username")  # Pass username as a query parameter
    user_preferences = mongo.db.user_preferences.find_one({"username": username})

    if not user_preferences:
        return jsonify({"message": "No preferences found!", "recommendations": []})

    # Extract user preferences
    preferred_style = user_preferences.get("preferences", {}).get("preferredStyle", "").lower()
    preferred_colors = user_preferences.get("preferences", {}).get("preferredColors", [])
    preferred_colors = [color.lower() for color in preferred_colors]

    # Filter the dataset based on preferences
    recommendations = dataset[
        (dataset["usage"].str.lower() == preferred_style)
        & (dataset["baseColour"].str.lower().isin(preferred_colors))
    ]

    recommendations = recommendations.head(50)
    # Get recommendations (assume images are named as "<id>.jpg")
    recommendation_list = [
        {
            "id": row["id"],
            "productName": row["productDisplayName"],
            "image": f"/static/images/{row['id']}.jpg"
        }
        for _, row in recommendations.iterrows()
    ]
    # Resize images
    image_paths = [os.path.join(STATIC_FOLDER, f"{row['id']}.jpg") for _, row in recommendations.iterrows()]
    resize_images(image_paths, RESIZED_FOLDER)

    if not recommendation_list:
        return jsonify({"message": "No matching recommendations found!", "recommendations": []})

    return jsonify({"message": "Recommendations found!", "recommendations": recommendation_list})

BASE_DIR = "Clothing"
CATEGORIES = {
    "male": os.path.join(BASE_DIR, "MenClothing"),
    "female": os.path.join(BASE_DIR, "WomenClothing")
}
@app.route('/get_images', methods=['POST'])
def get_images():
    data = request.get_json()
    gender = data.get("gender").lower()

    if gender not in CATEGORIES:
        return jsonify({"error": "Invalid gender"}), 400

    # Get image file names from the respective folder
    image_folder = CATEGORIES[gender]
    images = [f"/static/{gender}/{img}" for img in os.listdir(image_folder) if img.endswith(('png', 'jpg', 'jpeg','webp'))]

    return jsonify({"images": images})

if __name__ == "__main__":
    app.run(debug=True)