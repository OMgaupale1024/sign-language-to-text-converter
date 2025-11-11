# Quick Setup Guide

## Backend Setup (Python)

1. **Install Python dependencies:**
```bash
pip install flask flask-cors opencv-python pillow pyttsx3 tensorflow keras cvzone numpy
```

**Note:** If you encounter issues with TensorFlow/Keras, you may need:
```bash
pip install tensorflow==2.13.0
```

2. **Ensure model file exists:**
   - Make sure `cnn8grps_rad1_model.h5` is in the root directory
   - If not, you'll need to train or download the model

3. **Start the Flask server:**
```bash
python server.py
```

The server should start on `http://localhost:5000`

## Frontend Setup (React)

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Troubleshooting

### Backend Issues

- **ModuleNotFoundError**: Install missing Python packages
- **Model file not found**: Ensure `cnn8grps_rad1_model.h5` exists in root
- **Port already in use**: Change port in `server.py` (line 134)

### Frontend Issues

- **npm install fails**: Try `npm install --legacy-peer-deps`
- **Vite errors**: Clear node_modules and reinstall
- **CORS errors**: Ensure backend is running and CORS is enabled

### Camera Issues

- **Permission denied**: Allow camera access in browser settings
- **No video feed**: Check browser console for errors
- **HTTPS required**: Some browsers require HTTPS for camera (localhost is OK)

## Development Tips

1. **Backend logs**: Check Flask console for prediction logs
2. **Frontend logs**: Open browser DevTools (F12) to see React logs
3. **API testing**: Use browser DevTools Network tab to inspect API calls
4. **Debug mode**: Toggle debug panel to see hand skeleton visualization

## Production Build

To build for production:

```bash
# Frontend
npm run build

# The built files will be in the `dist/` directory
# Serve with any static file server or integrate with your backend
```

