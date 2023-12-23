from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from keras.preprocessing.text import Tokenizer
import pandas as pd
import pytesseract
from PIL import Image
import argparse

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Load the trained model
loaded_model = load_model("best_model.h5")  # Update the path accordingly

# Load CSV files
train_data = pd.read_csv('Training_meme_dataset.csv')

# Text processing
tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_data['sentence'])

max_sequence_length = 100  # Adjust as needed
vocab_size = len(tokenizer.word_index) + 1
# Function to preprocess a single image and text
# Function to preprocess a single image and text
# Function to preprocess a single image and text using pytesseract
def preprocess_single_image(image_path, tokenizer, max_sequence_length):
    # Load and preprocess the image
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    # Extract text using pytesseract
    text = pytesseract.image_to_string(Image.open(image_path))

    # Process the text
    sequences = tokenizer.texts_to_sequences([text])
    padded_sequences = pad_sequences(sequences, maxlen=max_sequence_length, padding='post')

    return img_array, padded_sequences

parser = argparse.ArgumentParser(description='Description of your script.')

parser.add_argument('image', type=str, help='Path to the image.')
args = parser.parse_args()

# Path to a single image
single_image_path = args.image
# Preprocess the single image and text
single_image, single_text_sequence = preprocess_single_image(single_image_path, tokenizer, max_sequence_length)

# Make the prediction using the loaded model
prediction = loaded_model.predict([single_image, single_text_sequence])

# Convert the prediction to a binary value (0 or 1) based on the threshold (e.g., 0.5)
binary_prediction = 1 if prediction > 0.4 else 0

# # Display the result
# print("Predicted Probability:", prediction[0, 0])
print("Binary Prediction:", binary_prediction)

