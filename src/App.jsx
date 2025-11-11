import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://localhost:5000'

function App() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentLetter, setCurrentLetter] = useState('—')
  const [confidence, setConfidence] = useState(0)
  const [outputText, setOutputText] = useState('')
  const [debugMode, setDebugMode] = useState(false)
  const [debugView, setDebugView] = useState('skeleton') // 'skeleton' or 'canvas'
  const [debugImage, setDebugImage] = useState(null)
  const [pendingLetter, setPendingLetter] = useState('')
  const [confirmMode, setConfirmMode] = useState(false)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        } 
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        
        // Wait for video to be ready before starting detection
        videoRef.current.onloadedmetadata = () => {
          console.log('Video ready, dimensions:', videoRef.current.videoWidth, 'x', videoRef.current.videoHeight)
          setIsStreaming(true)
          // Small delay to ensure video is fully ready
          setTimeout(() => {
            startDetection()
          }, 500)
        }
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('Failed to access camera. Please check permissions.')
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsStreaming(false)
    setCurrentLetter('—')
    setConfidence(0)
    setDebugImage(null)
  }

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) {
      console.log('Video or canvas not ready')
      return null
    }
    
    const video = videoRef.current
    const canvas = canvasRef.current
    
    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.log('Video not ready, readyState:', video.readyState)
      return null
    }
    
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.log('Video dimensions are zero')
      return null
    }
    
    const ctx = canvas.getContext('2d')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)
    
    return canvas.toDataURL('image/jpeg', 0.8)
  }

  const predictSign = async () => {
    const imageData = captureFrame()
    if (!imageData) {
      // Only log occasionally to avoid spam
      if (Math.random() < 0.01) {
        console.log('No image data captured')
      }
      return
    }

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('API response error:', errorData)
        throw new Error(errorData.error || 'Prediction failed')
      }

      const data = await response.json()
      
      if (data.error) {
        console.error('API error:', data.error)
        return
      }
      
      setCurrentLetter(data.text || '—')
      setConfidence(data.confidence || 0)
      
      // Always update debug image if available, not just in debug mode
      if (data.white_canvas) {
        setDebugImage(data.white_canvas)
      }
      
      // Log hand detection status occasionally
      if (data.hand_detected === false && Math.random() < 0.1) {
        console.log('No hand detected in frame')
      }
    } catch (error) {
      console.error('Prediction error:', error)
      // Don't update state on error to keep last valid prediction
    }
  }

  const startDetection = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(predictSign, 200) // 5 FPS
  }

  const handleCopy = () => {
    if (outputText.trim()) {
      navigator.clipboard.writeText(outputText)
      alert('Text copied to clipboard!')
    }
  }

  const handleSpeak = async () => {
    if (!outputText.trim()) return
    
    try {
      await fetch(`${API_URL}/speak`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: outputText }),
      })
    } catch (error) {
      console.error('Speak error:', error)
      // Fallback to browser TTS
      const utterance = new SpeechSynthesisUtterance(outputText)
      window.speechSynthesis.speak(utterance)
    }
  }

  const handleReset = () => {
    setOutputText('')
    setCurrentLetter('—')
    setConfidence(0)
    setPendingLetter('')
    pendingLetterRef.current = ''
    lastAddedLetterRef.current = ''
    letterStableCountRef.current = 0
    lastActionRef.current = ''
    confirmModeRef.current = false
    setConfirmMode(false)
  }

  const lastAddedLetterRef = useRef('')
  const letterStableCountRef = useRef(0)
  const lastActionRef = useRef('')
  const pendingLetterRef = useRef('') // Store letter waiting for confirmation
  const confirmModeRef = useRef(false) // Track if closed hand was shown (confirm mode)

  useEffect(() => {
    if (currentLetter && currentLetter !== '—' && confidence > 0.7) {
      // Handle special gestures
      if (currentLetter === 'Backspace') {
        if (lastActionRef.current !== 'Backspace') {
          setOutputText(prev => {
            if (prev.length > 0) {
              return prev.slice(0, -1)
            }
            return prev
          })
          lastActionRef.current = 'Backspace'
          pendingLetterRef.current = '' // Clear pending letter
          setPendingLetter('') // Clear pending letter state
          confirmModeRef.current = false // Clear confirm mode
          setConfirmMode(false) // Update state for UI
          console.log('Backspace gesture detected')
        }
        return
      }
      
      if (currentLetter === ' ' || currentLetter.trim() === '') {
        if (lastActionRef.current !== 'Space') {
          setOutputText(prev => {
            // Add space if last character is not already a space
            if (prev.slice(-1) !== ' ') {
              return prev + ' '
            }
            return prev
          })
          lastActionRef.current = 'Space'
          pendingLetterRef.current = '' // Clear pending letter
          setPendingLetter('') // Clear pending letter state
          confirmModeRef.current = false // Clear confirm mode
          setConfirmMode(false) // Update state for UI
          console.log('Space gesture detected')
        }
        return
      }
      
      // Handle "confirm" gesture (closed hand/fist) - sets confirm mode
      if (currentLetter === 'confirm') {
        if (lastActionRef.current !== 'Confirm') {
          confirmModeRef.current = true
          setConfirmMode(true) // Update state for UI
          lastActionRef.current = 'Confirm'
          console.log('Closed hand detected - confirm mode ON. Show letter again to add.')
        }
        return
      }
      
      // Handle regular letters
      if (currentLetter === lastAddedLetterRef.current) {
        letterStableCountRef.current += 1
        pendingLetterRef.current = currentLetter // Keep updating pending letter
        setPendingLetter(currentLetter) // Update pending letter state
        
        // Auto-add if stable for 3 frames
        if (letterStableCountRef.current >= 3) {
          setOutputText(prev => {
            // If in confirm mode and letter matches pending, add it (allows duplicates)
            if (confirmModeRef.current && currentLetter === pendingLetterRef.current) {
              lastAddedLetterRef.current = ''
              letterStableCountRef.current = 0
              lastActionRef.current = 'Letter'
              pendingLetterRef.current = ''
              setPendingLetter('') // Clear pending letter state
              confirmModeRef.current = false // Clear confirm mode
              setConfirmMode(false) // Update state for UI
              console.log('Letter confirmed and added:', currentLetter)
              return prev + currentLetter
            }
            // Only auto-add if different from last character
            if (prev.slice(-1) !== currentLetter) {
              lastAddedLetterRef.current = ''
              letterStableCountRef.current = 0
              lastActionRef.current = 'Letter'
              pendingLetterRef.current = ''
              setPendingLetter('') // Clear pending letter state
              confirmModeRef.current = false // Clear confirm mode
              setConfirmMode(false) // Update state for UI
              return prev + currentLetter
            }
            // If same as last and not in confirm mode, keep it as pending
            return prev
          })
        }
      } else {
        // New letter detected
        // If we were in confirm mode but got a different letter, clear confirm mode
        if (confirmModeRef.current && currentLetter !== pendingLetterRef.current) {
          confirmModeRef.current = false
          setConfirmMode(false) // Update state for UI
          console.log('Different letter shown - confirm mode cleared')
        }
        
        lastAddedLetterRef.current = currentLetter
        letterStableCountRef.current = 1
        pendingLetterRef.current = currentLetter // Store new letter as pending
        setPendingLetter(currentLetter) // Update pending letter state
        lastActionRef.current = ''
      }
    } else {
      // Reset when confidence is low
      if (confidence < 0.5) {
        lastAddedLetterRef.current = ''
        letterStableCountRef.current = 0
        lastActionRef.current = ''
        // Don't clear confirm mode on low confidence - user might still be closing hand
      }
    }
  }, [currentLetter, confidence])

  return (
    <div className="min-h-screen bg-black text-white font-mono">
      {/* Header */}
      <header className="border-b-4 border-white p-6">
        <h1 className="text-4xl font-bold tracking-wider uppercase">
          SignSpeak
        </h1>
        <p className="text-sm mt-2 opacity-80">REAL-TIME SIGN LANGUAGE DETECTION</p>
      </header>

      <div className="container mx-auto p-6 space-y-6">
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Camera Preview Section */}
          <div className="lg:col-span-2 space-y-4">
            <div className="border-4 border-white bg-black p-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold uppercase">Camera Feed</h2>
                {!isStreaming ? (
                  <button
                    onClick={startCamera}
                    className="px-6 py-2 border-4 border-white bg-white text-black font-bold uppercase hover:bg-black hover:text-white transition-all"
                  >
                    Start
                  </button>
                ) : (
                  <button
                    onClick={stopCamera}
                    className="px-6 py-2 border-4 border-red-500 bg-red-500 text-white font-bold uppercase hover:bg-black hover:text-red-500 transition-all"
                  >
                    Stop
                  </button>
                )}
              </div>
              
              <div className="relative bg-black border-2 border-white aspect-video overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
                <canvas ref={canvasRef} className="hidden" />
                
                {!isStreaming && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black">
                    <p className="text-xl opacity-50">CAMERA OFF</p>
                  </div>
                )}
              </div>
            </div>

            {/* Letter Recognition Bubble */}
            <div className="border-4 border-white bg-black p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase opacity-70 mb-2">Detected Gesture</p>
                  <div className="text-8xl font-bold tracking-wider">
                    {currentLetter === 'Backspace' ? '⌫' : 
                     currentLetter === ' ' ? 'SPACE' : 
                     currentLetter === 'confirm' ? '✓' :
                     currentLetter}
                  </div>
                  {currentLetter === 'Backspace' && (
                    <p className="text-xs uppercase mt-2 text-yellow-400">Backspace</p>
                  )}
                  {currentLetter === ' ' && (
                    <p className="text-xs uppercase mt-2 text-yellow-400">Space</p>
                  )}
                  {currentLetter === 'confirm' && (
                    <p className="text-xs uppercase mt-2 text-green-400">Confirm</p>
                  )}
                  {pendingLetter && currentLetter !== 'confirm' && currentLetter !== 'Backspace' && currentLetter !== ' ' && currentLetter === pendingLetter && (
                    <p className="text-xs uppercase mt-2 text-blue-400">
                      {confirmMode ? (
                        <>Ready: Show {pendingLetter} again to add</>
                      ) : (
                        <>Pending: {pendingLetter} (Close hand, then show {pendingLetter} again)</>
                      )}
                    </p>
                  )}
                  {confirmMode && (!pendingLetter || currentLetter === 'confirm') && (
                    <p className="text-xs uppercase mt-2 text-green-400">
                      ✓ Confirm Mode: Show letter again to add
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-sm uppercase opacity-70 mb-2">Confidence</p>
                  <div className="text-4xl font-bold">
                    {Math.round(confidence * 100)}%
                  </div>
                  <div className="mt-4 w-32 h-4 border-2 border-white bg-black overflow-hidden">
                    <div
                      className="h-full bg-white transition-all duration-300"
                      style={{ width: `${confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Output Text Section */}
          <div className="space-y-4">
            <div className="border-4 border-white bg-black p-4">
              <h2 className="text-2xl font-bold uppercase mb-4">Output Text</h2>
              <textarea
                value={outputText}
                onChange={(e) => setOutputText(e.target.value)}
                className="w-full h-48 p-4 border-4 border-white bg-black text-white font-mono text-lg resize-none focus:outline-none focus:border-yellow-400"
                placeholder="Detected text will appear here..."
              />
              
              <div className="flex gap-2 mt-4">
                <button
                  onClick={handleCopy}
                  disabled={!outputText.trim()}
                  className="flex-1 px-4 py-3 border-4 border-white bg-white text-black font-bold uppercase hover:bg-black hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Copy
                </button>
                <button
                  onClick={handleSpeak}
                  disabled={!outputText.trim()}
                  className="flex-1 px-4 py-3 border-4 border-white bg-white text-black font-bold uppercase hover:bg-black hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Speak
                </button>
                <button
                  onClick={handleReset}
                  className="flex-1 px-4 py-3 border-4 border-red-500 bg-red-500 text-white font-bold uppercase hover:bg-black hover:text-red-500 transition-all"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Gesture Guide */}
            <div className="border-4 border-white bg-black p-4">
              <h2 className="text-xl font-bold uppercase mb-3">Gestures</h2>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="opacity-70">Backspace:</span>
                  <span className="font-bold">B/C/H/F/X + Thumb Up</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Space:</span>
                  <span className="font-bold">E/S/X/Y/B + Middle Fingers</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Confirm:</span>
                  <span className="font-bold text-green-400">Close Hand (Fist)</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Letters:</span>
                  <span className="font-bold">A-Z Signs</span>
                </div>
                <div className="mt-3 pt-3 border-t-2 border-white">
                  <p className="text-xs opacity-60">
                    Tip: Close hand (fist), then show letter again to add same letter twice (e.g., "LL" in HELLO)
                  </p>
                </div>
              </div>
            </div>

            {/* Debug Panel Toggle */}
            <div className="border-4 border-white bg-black p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold uppercase">Debug Panel</h2>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={debugMode}
                    onChange={(e) => setDebugMode(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-14 h-8 border-4 border-white bg-black peer-checked:bg-white transition-all">
                    <div className="w-6 h-6 bg-white mt-0.5 ml-0.5 peer-checked:ml-6 transition-all" />
                  </div>
                </label>
              </div>

              {debugMode && (
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setDebugView('skeleton')}
                      className={`flex-1 px-4 py-2 border-4 font-bold uppercase transition-all ${
                        debugView === 'skeleton'
                          ? 'border-white bg-white text-black'
                          : 'border-white bg-black text-white hover:bg-white hover:text-black'
                      }`}
                    >
                      Skeleton
                    </button>
                    <button
                      onClick={() => setDebugView('canvas')}
                      className={`flex-1 px-4 py-2 border-4 font-bold uppercase transition-all ${
                        debugView === 'canvas'
                          ? 'border-white bg-white text-black'
                          : 'border-white bg-black text-white hover:bg-white hover:text-black'
                      }`}
                    >
                      Canvas
                    </button>
                  </div>

                  {debugImage ? (
                    <div className="border-2 border-white bg-black aspect-square overflow-hidden">
                      <img
                        src={debugImage}
                        alt="Debug view"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    <div className="border-2 border-white bg-black aspect-square flex items-center justify-center">
                      <p className="text-sm opacity-50">No debug data</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="border-4 border-white bg-black p-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <span className="uppercase">Status:</span>
              <span className={isStreaming ? 'text-green-400' : 'text-red-400'}>
                {isStreaming ? '● STREAMING' : '○ IDLE'}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span className="uppercase">API:</span>
              <span className="opacity-70">{API_URL}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

