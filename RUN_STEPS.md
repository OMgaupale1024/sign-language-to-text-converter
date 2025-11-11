# Step-by-Step Guide to Run SignSpeak

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 18 or higher installed
- ✅ npm (comes with Node.js)
- ✅ Webcam connected and working
- ✅ Model file `cnn8grps_rad1_model.h5` in the root directory

## Step 1: Install Backend Dependencies

Open a terminal/command prompt in the project root directory and run:

```bash
pip install flask flask-cors opencv-python pillow pyttsx3 tensorflow keras cvzone numpy
```

**Note for Windows users:** If you get errors, try:
```bash
pip install --upgrade pip
pip install flask flask-cors opencv-python pillow pyttsx3 tensorflow keras cvzone numpy
```

**Note for TensorFlow issues:** If TensorFlow installation fails, try:
```bash
pip install tensorflow==2.13.0
```

## Step 2: Verify Model File

Check that the model file exists:
```bash
# Windows
dir cnn8grps_rad1_model.h5

# Mac/Linux
ls -la cnn8grps_rad1_model.h5
```

If the file doesn't exist, you'll need to obtain it or train the model first.

## Step 3: Start the Backend Server

In the same terminal, run:

```bash
python server.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
```

**Keep this terminal window open!** The server must stay running.

## Step 4: Install Frontend Dependencies

Open a **NEW** terminal/command prompt window in the same project directory and run:

```bash
npm install
```

This will install React, Vite, Tailwind CSS, and other dependencies. Wait for it to complete (may take 1-2 minutes).

**If you get errors**, try:
```bash
npm install --legacy-peer-deps
```

## Step 5: Start the Frontend Development Server

In the same terminal (where you ran `npm install`), run:

```bash
npm run dev
```

You should see output like:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## Step 6: Open the Application

1. Open your web browser (Chrome, Firefox, Edge, or Safari)
2. Navigate to: `http://localhost:3000`
3. You should see the SignSpeak interface

## Step 7: Grant Camera Permissions

When you click the **"Start"** button:
1. Your browser will ask for camera permission
2. Click **"Allow"** or **"Yes"** to grant access
3. Your camera feed should appear in the preview area

## Step 8: Test the Application

1. Click **"Start"** button to begin camera feed
2. Position your hand in front of the camera
3. Show sign language letters (A-Z)
4. Watch the letter recognition bubble for detected letters
5. Letters will automatically be added to the output text when confidence is high
6. Try the **Copy**, **Speak**, and **Reset** buttons
7. Toggle the **Debug Panel** to see hand skeleton visualization

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'flask'`
- **Solution:** Run `pip install flask flask-cors opencv-python pillow pyttsx3 tensorflow keras cvzone numpy`

**Problem:** `FileNotFoundError: cnn8grps_rad1_model.h5`
- **Solution:** Ensure the model file is in the root directory with `server.py`

**Problem:** `Address already in use` (port 5000)
- **Solution:** 
  - Close any other application using port 5000
  - Or edit `server.py` line 134 to use a different port: `app.run(host='0.0.0.0', port=5001)`

**Problem:** `cvzone` module not found
- **Solution:** Install with `pip install cvzone`

### Frontend Issues

**Problem:** `npm install` fails
- **Solution:** Try `npm install --legacy-peer-deps` or update Node.js

**Problem:** `npm run dev` shows port 3000 already in use
- **Solution:** 
  - Close other applications using port 3000
  - Or edit `vite.config.js` to use a different port

**Problem:** Page shows "Cannot connect to API"
- **Solution:** 
  - Ensure backend server is running (Step 3)
  - Check that backend is on `http://localhost:5000`
  - Check browser console (F12) for CORS errors

### Camera Issues

**Problem:** Camera permission denied
- **Solution:** 
  - Check browser settings for camera permissions
  - Use `localhost` (not `127.0.0.1`)
  - Some browsers require HTTPS (localhost is exempt)

**Problem:** Black screen in camera preview
- **Solution:** 
  - Check if another app is using the camera
  - Try refreshing the page
  - Check browser console (F12) for errors

**Problem:** No letter detection
- **Solution:** 
  - Ensure good lighting
  - Position hand clearly in frame
  - Check backend terminal for errors
  - Verify model file exists and is correct

## Quick Command Reference

```bash
# Terminal 1 - Backend
python server.py

# Terminal 2 - Frontend
npm install
npm run dev
```

## Stopping the Application

1. **Stop Frontend:** Press `Ctrl+C` in the frontend terminal
2. **Stop Backend:** Press `Ctrl+C` in the backend terminal
3. **Close browsers:** Close the browser tab

## Next Steps

- Adjust detection sensitivity in `src/App.jsx` (confidence threshold)
- Modify UI colors in `src/App.jsx` (brutalist design elements)
- Add more features like word suggestions
- Customize the debug panel visualization

## Need Help?

- Check `README.md` for detailed documentation
- Check `SETUP.md` for additional setup tips
- Review browser console (F12) for error messages
- Check backend terminal for Python errors

