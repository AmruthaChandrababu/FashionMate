import os
import cv2
import numpy as np
from tensorflow.keras.applications import InceptionResNetV2 # type: ignore
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input, decode_predictions # type: ignore
from tensorflow.keras.models import Model # type: ignore

class ClothingClassifier:
    def __init__(self):
        # Load Pre-Trained Model
        self.base_model = InceptionResNetV2(weights="imagenet", include_top=True)
        self.feature_extractor = Model(
            inputs=self.base_model.input,
            outputs=self.base_model.get_layer("avg_pool").output
        )
    
    def preprocess_image(self, image_path):
        """Preprocess an image for the model input."""
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (299, 299))  # InceptionResNetV2 requires 299x299 input size
        image = preprocess_input(image)  # Normalize for InceptionResNetV2
        return np.expand_dims(image, axis=0)  # Add batch dimension
    
    def classify_clothing(self, image_path):
        """Predicts clothing type using the pre-trained model."""
        image = self.preprocess_image(image_path)
        predictions = self.base_model.predict(image)
        decoded_predictions = decode_predictions(predictions, top=3)[0]
        return {
            "top_predictions": [
                {"class": pred[1], "probability": float(pred[2])}
                for pred in decoded_predictions
            ],
            "most_likely_class": decoded_predictions[0][1]
        }
    
    def extract_features(self, image_path):
        """Extract features from the image for recommendation purposes."""
        image = self.preprocess_image(image_path)
        features = self.feature_extractor.predict(image)
        return features.tolist()
    
    def custom_clothing_categories(self, predicted_class):
        """Map predicted classes to custom clothing categories."""
        category_mapping = {
            't-shirt': 'Top',
            'shirt': 'Top',
            'jean': 'Bottom',
            'jacket': 'Outerwear',
            'dress': 'One-piece',
            'skirt': 'Bottom',
            'sweater': 'Outerwear',
        }
        return category_mapping.get(predicted_class.lower(), 'Uncategorized')

    def recommend_outfits(self, predicted_class):
        """Provide recommendations based on the predicted clothing type."""
        recommendations = {
            't-shirt': "Pair with casual jeans or shorts for a relaxed look.",
            'shirt': "Style with formal trousers or a skirt for a polished look.",
            'jean': "Combine with a simple t-shirt or a button-up shirt.",
            'jacket': "Layer over a t-shirt or dress for a trendy and warm look.",
            'dress': "Add a stylish cardigan and heels for a chic outfit.",
            'skirt': "Pair with a tucked-in blouse or a casual top for balance.",
            'sweater': "Perfect with skinny jeans or a skirt for a cozy outfit.",
        }
        return recommendations.get(predicted_class.lower(), "Style it based on your preferences!")
