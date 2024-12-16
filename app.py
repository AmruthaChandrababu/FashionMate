from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models.clothing_classifier import ClothingClassifier
from database.mongo_connection import MongoDBConnection
from models.user_model import User
import os

# Flask app initialization
app = Flask(
    __name__,
    template_folder='assets/templates',
    static_folder='assets/static'
)


app.secret_key = 'supersecretkey'

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'assets', 'uploads')  # Absolute path to avoid issues

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# MongoDB connection and classifier initialization
mongo_conn = MongoDBConnection()
clothing_classifier = ClothingClassifier()

# Routes
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        preferences = request.form.getlist('preferences')
        
        # Check if user exists
        if mongo_conn.get_user(username):
            return "User already exists!"

        # Register user
        user = User(username=username, password=password, preferences=preferences)
        mongo_conn.register_user(user)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = mongo_conn.get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Invalid username or password!"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/wardrobe')
def view_wardrobe():
    """Render the My Wardrobe page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('my_wardrobe.html')  # Page will dynamically load data via JavaScript

@app.route('/wardrobe_data', methods=["GET"])
def fetch_wardrobe_data():
    """API to fetch all wardrobe items for the logged-in user."""
    if 'user' not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session['user']
    wardrobe_items = mongo_conn.get_user_wardrobe(user_id)
    return jsonify(wardrobe_items)

@app.route('/upload_item', methods=["POST"])
def upload_wardrobe_item():
    """API to upload, classify, and save a new wardrobe item."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 403

    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Classify the uploaded image
    classification = clothing_classifier.classify_clothing(filepath)
    category = clothing_classifier.custom_clothing_categories(
        classification.get('most_likely_class', 'Uncategorized')
    )

    # Save the wardrobe item in the database
    wardrobe_item = {
        "filename": filename,
        "classification": classification,
        "category": category,
        "user_id": session['user']
    }
    result = mongo_conn.insert_wardrobe_item(session['user'], wardrobe_item)
    wardrobe_item["_id"] = str(result.inserted_id)  # Convert ObjectId to string

    # Generate recommendations
    wardrobe_items = mongo_conn.get_user_wardrobe(session['user'])
    for item in wardrobe_items:
        item["_id"] = str(item["_id"])  # Convert all ObjectId to string
    recommendations = generate_recommendations(classification, wardrobe_items)

    return jsonify({
        "message": "Item uploaded and classified successfully.",
        "uploaded_item": wardrobe_item,
        "recommendations": recommendations
    })




# Add a new route to serve images from the uploads directory
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))



def generate_recommendations(uploaded_item, wardrobe_items):
    """
    Recommend wardrobe items based on the uploaded item's classification and category.
    """
    uploaded_category = uploaded_item.get('most_likely_class', '').lower()

    # Define pairing logic (customize as needed)
    pairings = {
        'top': ['bottom', 'outerwear'],
        'bottom': ['top', 'outerwear'],
        'one-piece': ['outerwear'],
        'outerwear': ['top', 'bottom'],
        'uncategorized': []  # No recommendations for uncategorized items
    }

    recommendations = [
        item for item in wardrobe_items
        if item['category'].lower() in pairings.get(uploaded_category, [])
    ]
    return recommendations


@app.route('/recommendations')
def recommendations():
    if 'user' not in session:
        return redirect(url_for('login'))
    recommendations = []  # Placeholder for recommendations logic
    return render_template('recommendations.html', recommendations=recommendations)

@app.route('/tryon')
def tryon():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('tryon.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = mongo_conn.get_user(session['user'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('homepage'))
@app.route('/debug-static-path')
def debug_static_path():
    return jsonify({
        "static_folder": app.static_folder,
        "static_files": os.listdir(os.path.join(app.static_folder, 'js'))
    })

if __name__ == '__main__':
    app.run(debug=True)
