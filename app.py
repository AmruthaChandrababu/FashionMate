from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

# Import custom modules
from models.clothing_classifier import ClothingClassifier
from database.mongodb_connection import MongoDBConnection

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Initialize services
clothing_classifier = ClothingClassifier()
mongo_conn = MongoDBConnection()

@app.route('/upload_clothing', methods=['POST'])
def upload_clothing():
    """
    API endpoint to upload and classify clothing items
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Secure filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Classify clothing
            classification = clothing_classifier.classify_clothing(filepath)
            
            # Get custom category
            category = clothing_classifier.custom_clothing_categories(
                classification['most_likely_class']
            )
            
            # Prepare wardrobe item data
            wardrobe_item = {
                'filename': filename,
                'classification': classification,
                'category': category
            }
            
            # Insert into MongoDB (assuming user_id is passed)
            user_id = request.form.get('user_id', 'default_user')
            mongo_conn.insert_wardrobe_item(user_id, wardrobe_item)
            
            return jsonify({
                'message': 'Clothing uploaded successfully',
                'classification': classification,
                'category': category
            }), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Upload failed'}), 400

@app.route('/user/wardrobe', methods=['GET'])
def get_user_wardrobe():
    """
    API endpoint to retrieve user's wardrobe
    """
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        wardrobe_items = mongo_conn.get_user_wardrobe(user_id)
        return jsonify({
            'wardrobe': wardrobe_items,
            'total_items': len(wardrobe_items)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    API endpoint to get outfit recommendations
    """
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        # Placeholder for recommendation logic
        # In a full implementation, this would use more sophisticated recommendation algorithms
        user_wardrobe = mongo_conn.get_user_wardrobe(user_id)
        
        # Simple recommendation (just return top 3 items)
        recommendations = user_wardrobe[:3]
        
        return jsonify({
            'recommendations': recommendations
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """
    Error handler for file upload size limit
    """
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, port=5000)