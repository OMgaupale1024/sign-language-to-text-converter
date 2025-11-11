# SignSpeak Web App

A modern, brutalist-style web application for real-time sign language detection using React, Tailwind CSS, and a Flask backend.

## Features

- 🎥 **Real-time Camera Preview** - Live video feed from your webcam
- 🔤 **Live Letter Recognition** - Displays detected sign language letters in real-time
- 📊 **Confidence Meter** - Visual indicator showing prediction confidence
- 📝 **Output Text Box** - Accumulates detected letters into text
- 🔧 **Action Buttons** - Copy, Speak (TTS), and Reset functionality
- 🐛 **Debug Panel** - Toggle to view hand skeleton or white canvas visualization
- 🎨 **Brutalist Design** - Clean, bold, monospace typography with high contrast

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Webcam access

## Backend Setup

1. Install Python dependencies:
```bash
pip install flask flask-cors opencv-python pillow pyttsx3 tensorflow keras cvzone numpy
```

2. Make sure you have the model file `cnn8grps_rad1_model.h5` in the root directory

3. Start the Flask server:
```bash
python server.py
```

The server will run on `http://localhost:5000`

## Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## API Endpoints

### POST `/predict`
Predicts sign language letter from an image and returns debug visualization.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "text": "A",
  "confidence": 0.95,
  "white_canvas": "data:image/jpeg;base64,...",
  "skeleton": "data:image/jpeg;base64,..."
}
```

### POST `/detect`
Simple detection endpoint (without debug data).

### POST `/speak`
Text-to-speech endpoint.

## Project Structure

```
sign-language-to-text-converter/
├── server.py              # Flask backend with /predict endpoint
├── src/
│   ├── App.jsx           # Main React component
│   ├── main.jsx          # React entry point
│   └── index.css         # Tailwind CSS styles
├── package.json          # Node.js dependencies
├── tailwind.config.js    # Tailwind configuration
├── vite.config.js        # Vite configuration
└── index.html           # HTML template
```

## Usage

1. Start both backend and frontend servers
2. Click "Start" to begin camera feed
3. Show sign language letters to your webcam
4. Detected letters will appear in the recognition bubble
5. Letters are automatically added to the output text when confidence is high
6. Use Copy/Speak/Reset buttons to manage the output text
7. Toggle Debug Panel to view hand skeleton visualization

## Design Philosophy

The UI follows a brutalist design aesthetic:
- **Bold borders** - Thick, high-contrast borders (4px)
- **Monospace typography** - Courier New font throughout
- **High contrast** - Black background with white elements
- **Minimal decoration** - Clean, functional design
- **Uppercase text** - Headers and labels in uppercase
- **Geometric shapes** - Square buttons and panels

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari (may require additional permissions)

## Troubleshooting

- **Camera not working**: Check browser permissions and ensure HTTPS (or localhost)
- **API errors**: Verify backend is running on port 5000
- **Model not found**: Ensure `cnn8grps_rad1_model.h5` is in the root directory
- **CORS errors**: Backend includes CORS headers, but check firewall settings

## License

MIT

