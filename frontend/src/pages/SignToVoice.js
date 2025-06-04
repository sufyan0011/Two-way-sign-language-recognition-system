import React, { useState, useRef, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const GestureToSpeech = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [sentence, setSentence] = useState("");
  const [currentGesture, setCurrentGesture] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const lastAddedTimeRef = useRef(0);

  // Gesture prediction interval
  useEffect(() => {
    const interval = setInterval(() => {
      processGesture();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Camera initialization
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        videoRef.current.srcObject = stream;
      } catch (err) {
        setError("Camera access denied. Please enable permissions.");
      }
    };
    startCamera();
  }, []);

  const processGesture = async () => {
    try {
      const canvas = canvasRef.current;
      const video = videoRef.current;

      if (!canvas || !video) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);

      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.8)
      );

      const formData = new FormData();
      formData.append("image", blob, "gesture.jpg");

      const response = await fetch(
        "http://10.91.53.106:5003/process-gesture",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Gesture recognition failed");

      const data = await response.json();
      if (data.prediction) updateSentence(data.prediction);
    } catch (err) {
      setError(err.message);
    }
  };

  const updateSentence = (gesture) => {
    const now = Date.now();
    if (now - lastAddedTimeRef.current < 2000) return;
    lastAddedTimeRef.current = now;

    setSentence((prev) => {
      if (gesture === "space") return prev.trim() + " ";
      if (gesture === "BACKSPACE") return prev.slice(0, -1);
      return prev + gesture;
    });
    setCurrentGesture(gesture);
  };

  const generateSpeech = async () => {
    if (!sentence) {
      setError("Please enter some text first");
      return;
    }

    setIsProcessing(true);
    setError("");

    try {
      // Clear previous audio
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
        setAudioUrl("");
      }

      const response = await fetch("http://10.91.53.106:5003/text-to-speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sentence }),
      });

      if (!response.ok) throw new Error("Audio generation failed");

      const blob = await response.blob();
      const newAudioUrl = URL.createObjectURL(blob);
      setAudioUrl(newAudioUrl);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // Cleanup audio URLs on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  return (
    <div
      className="d-flex flex-column chat-background w-100"
      style={{
        backgroundColor: "#e6e6e6" /* Light gray for WhatsApp-like feel */,
        backgroundImage:
          'url("https://www.transparenttextures.com/patterns/inspiration-geometry.png")',
        backgroundRepeat: "repeat",
        backgroundSize: "contain",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div className="container mt-5">
        <h1 className="mb-4 text-center">Gesture to Speech Converter</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="card shadow mb-4">
          <div className="card-body text-center">
            <div className="w-100" style={{ maxWidth: "100%" }}>
              <video
                ref={videoRef}
                autoPlay
                muted
                className="img-fluid rounded" // Ensures the video fills the available width
              />
            </div>
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </div>
        </div>

        <div className="card shadow mb-4">
          <div className="card-body">
            <h3 className="text-primary">Recognized Text</h3>
            <div className="alert alert-secondary fs-5">
              {sentence || "Perform gestures in front of camera..."}
            </div>
            <div className="d-grid gap-2 d-md-block">
              <button
                className="btn btn-warning me-2"
                onClick={() => setSentence((p) => p.slice(0, -1))}
              >
                Backspace
              </button>
              <button
                className="btn btn-danger"
                onClick={() => setSentence("")}
              >
                Clear All
              </button>
            </div>
          </div>
        </div>

        <div className="card shadow mb-5">
          <div className="card-body">
            <h4 className="text-success">
              Current Gesture: {currentGesture || "None"}
            </h4>

            <button
              className="btn btn-primary mt-3"
              onClick={generateSpeech}
              disabled={isProcessing || !sentence}
            >
              {isProcessing ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2"></span>
                  Generating Speech...
                </>
              ) : (
                "Convert to Speech"
              )}
            </button>

            {audioUrl && (
              <div className="mt-4">
                <audio
                  controls
                  className="w-100 mb-3"
                  key={audioUrl} // Force re-render with new audio
                  autoPlay // Auto-play new audio
                >
                  <source src={audioUrl} type="audio/mpeg" />
                </audio>
                <a
                  href={audioUrl}
                  download="sign-language-speech.mp3"
                  className="btn btn-success"
                >
                  Download Audio
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GestureToSpeech;
