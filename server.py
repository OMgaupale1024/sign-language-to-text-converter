from flask import Flask, request, jsonify
from flask_cors import CORS
import base64, cv2, numpy as np, io
from PIL import Image
import pyttsx3
from keras.models import load_model

# Load model once
model = load_model('cnn8grps_rad1_model.h5')
classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

app = Flask(__name__)
CORS(app)
tts = pyttsx3.init()

def predict_sign(frame):
    resized = cv2.resize(frame, (400, 400))
    normalized = resized / 255.0
    reshaped = np.expand_dims(normalized, axis=0)
    result = model.predict(reshaped)
    predicted_class = classes[np.argmax(result)]
    return predicted_class

@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'no image provided'}), 400

    img_data = base64.b64decode(data['image'].split(',')[1])
    img = Image.open(io.BytesIO(img_data)).convert('RGB')
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    predicted = predict_sign(frame)
    return jsonify({'text': predicted, 'confidence': 0.9})

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    if text:
        tts.say(text)
        tts.runAndWait()
    return jsonify({'message': 'spoken'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
